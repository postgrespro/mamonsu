# -*- coding: utf-8 -*-

from mamonsu.lib.plugin import Plugin
from mamonsu.plugins.pgsql.pool import Pooler


# Считаем нагрузку по количеству выполняемых запросов в БД
class SparkmesActivity(Plugin):
    # execute method run() every 60s
    Interval = 60
    Coef = 0.4
    # key, zbx_key, description, units, delta, field_position  value_type
    #   0      1         2         3      4          5             6
    Items = [
        ('calls_upd', 'pgsql.queries.sparkmes', 'число запросов (modify)', 'n/m', Plugin.DELTA.simple_change, 1, Plugin.VALUE_TYPE.numeric_unsigned),
        ('calls_sel', 'pgsql.queries.sparkmes', 'число запросов (select)', 'n/m', Plugin.DELTA.simple_change, 1, Plugin.VALUE_TYPE.numeric_unsigned),

        ('time_upd', 'pgsql.queries.sparkmes', 'время (modify)', Plugin.UNITS.ms, Plugin.DELTA.simple_change, 2, Plugin.VALUE_TYPE.numeric_float),
        ('time_sel', 'pgsql.queries.sparkmes', 'время (select)', Plugin.UNITS.ms, Plugin.DELTA.simple_change, 2, Plugin.VALUE_TYPE.numeric_float),

        ('callsfirm', 'pgsql.queries.sparkmes', 'число запросов (firm)', 'n/m', Plugin.DELTA.simple_change, 1, Plugin.VALUE_TYPE.numeric_unsigned),
        ('callsip_s', 'pgsql.queries.sparkmes', 'число запросов (ip)',   'n/m', Plugin.DELTA.simple_change, 1, Plugin.VALUE_TYPE.numeric_unsigned),

        ('timefirm', 'pgsql.queries.sparkmes', 'время (firm)', Plugin.UNITS.ms, Plugin.DELTA.simple_change, 2, Plugin.VALUE_TYPE.numeric_float),
        ('timeip_s', 'pgsql.queries.sparkmes', 'время (ip)',   Plugin.UNITS.ms, Plugin.DELTA.simple_change, 2, Plugin.VALUE_TYPE.numeric_float),
    ]
    # name, type, ('graph item', color, yaxisside, drawtype)
    #   0     1         2.0        2.1     2.2       2.3
    Graphs = [
        ('sparkmes активность (calls)', 0, (('calls_upd',       'CCFFCC', 1, 5),
                                            ('calls_sel',       'CCFFFF', 1, 5),
                                            ('calls_upd_Yprev', '009900', 1, 2),
                                            ('calls_sel_Yprev', '009999', 1, 2),),),
        ('sparkmes активность (time)', 0,  (('time_upd',        'CCFFCC', 1, 5),
                                            ('time_sel',        'CCFFFF', 1, 5),
                                            ('time_upd_Yprev',  '009900', 1, 2),
                                            ('time_sel_Yprev',  '009999', 1, 2),),),
        ('sparkmes поиск (calls)', 0, (('callsfirm',       'CCFFCC', 1, 5),
                                       ('callsip_s',       'CCFFFF', 0, 5),
                                       ('callsfirm_Yprev', '009900', 1, 2),
                                       ('callsip_s_Yprev', '009999', 0, 2),),),
        ('sparkmes поиск (time)', 0, (('timefirm',         'CCFFCC', 1, 5),
                                      ('timeip_s',         'CCFFFF', 0, 5),
                                      ('timefirm_Yprev',   '009900', 1, 2),
                                      ('timeip_s_Yprev',   '009999', 0, 2),),),
    ]
    Yprev = [None] * len(Items)

    def run(self, zbx):
        # execute query on default database
        result = Pooler.query("""
        SELECT '_upd' as type,
               sum(calls) as calls,
               sum(total_time) as totaltime
        FROM pg_stat_statements
        where dbid = (select datid from pg_stat_database where datname = 'sparkmes')
          and left(query,8) = 'SELECT *' and query ~* '_UPDATE'
        union all
        SELECT '_sel' as type,
               sum(calls) as calls,
               sum(total_time) as totaltime
        FROM pg_stat_statements
        where dbid = (select datid from pg_stat_database where datname = 'sparkmes')
          and left(query,8) = 'SELECT *' and not (query ~* '_UPDATE')
        union all
		select substring(query,15,4) as type, sum(calls) as calls, sum(total_time) as totaltime
		FROM pg_stat_statements 
		where dbid = (select datid from pg_stat_database where datname = 'sparkmes') 
		  and (left(query,27) = 'SELECT * FROM firms_select('
		       OR
		       left(query,26) = 'SELECT * FROM ip_select((('
		      )
		group by 1
        """, 'sparkmes')
        # send a resulting value to zabbix
        for idx, item in enumerate(self.Items):
            key, zbxkey, val, delta = item[0], item[1], 0, item[4]
            #self.log.info('{0}[{1}] '.format(zbxkey, key)+str(idx))
            for row in result:
                if key.endswith(row[0]):
                    val = row[item[5]]
                    if self.Yprev[idx] is None:
                        self.Yprev[idx] = float(val)
                    self.Yprev[idx] = round(self.Coef * float(val) + (1 - self.Coef) * self.Yprev[idx], 1)
                    break
                else:
                    continue
            else:
                if self.Yprev[idx] is not None:
                    self.Yprev[idx] = self.Yprev[idx]/3  # исходных данных нет, уменьшаем значение
            if self.Yprev[idx] is None or self.Yprev[idx] is not None and self.Yprev[idx] <= 0:
                self.Yprev[idx] = None
            else:
                if val is not None:
                    if item[6] == Plugin.VALUE_TYPE.numeric_float:
                        zbx.send('{0}[{1}]'.format(zbxkey, key), float(val), delta)
                        self.log.info('{0}[{1}] '.format(zbxkey, key)+str(val))
                    else:
                        zbx.send('{0}[{1}]'.format(zbxkey, key), int(val), delta)
                        self.log.info('{0}[{1}] '.format(zbxkey, key)+str(val))
                    zbx.send('{0}[{1}_Yprev]'.format(zbxkey, key), float(self.Yprev[idx]), delta)
                    self.log.info('{0}[{1}_Yprev] '.format(zbxkey, key)+str(self.Yprev[idx]))
                # debug...
                #if key == 'calls_upd':

    # Declare zabbix items for template
    def items(self, template):
        result = ''
        for idx, item in enumerate(self.Items):
            key, zbxkey = item[0], item[1]
            result += template.item({
                'name': 'sparkmes: {0}'.format(item[2]),
                'key': zbxkey + ('[{0}]'.format(key)),
                'units': item[3],
                'value_type': item[6]
            })
            result += template.item({
                'name': 'sparkmes: {0}_Yprev'.format(item[2]),
                'key': zbxkey + ('[{0}_Yprev]'.format(key)),
                'units': item[3],
                'value_type': Plugin.VALUE_TYPE.numeric_float
            })
        return result

    # Declare zabbix graphs for template
    def graphs(self, template):
        result = ''
        for name in self.Graphs:
            items = []
            for idx, item in enumerate(name[2]):
                zbxkey =  'pgsql.queries.sparkmes[{0}]'.format(item[0])
                if item[3] is None:
                    items.append({
                        'key': zbxkey,
                        'color': item[1],
                        'yaxisside': item[2],
                        'sortorder': idx
                    })
                else:
                    items.append({
                        'key': zbxkey,
                        'color': item[1],
                        'yaxisside': item[2],
                        'drawtype': item[3],
                        'sortorder': idx
                    })
            graph = {'name': name[0], 'items': items, 'type': name[1]}
            result += template.graph(graph)

        return result
