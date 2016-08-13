# -*- coding: utf-8 -*-

from mamonsu.lib.plugin import Plugin
from mamonsu.plugins.pgsql.pool import Pooler


# Считаем нагрузку по количеству выполняемых запросов в БД
class Activity(Plugin):
    # execute method run() every 60s
    Interval = 60
    Yprev = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    Coef = 0.5
    # key, zbx_key, description, units, delta, field_position
    #   0      1         2         3      4          5
    Items = [
        ('calls_upd', 'pgsql.queries.test',
            'число запросов (modify)', 'n/m', Plugin.DELTA.simple_change, 1),
        ('calls_sel', 'pgsql.queries.test',
            'число запросов (select)', 'n/m', Plugin.DELTA.simple_change, 1),

        ('time_upd', 'pgsql.queries.test',
            'время (modify)', 'ms', Plugin.DELTA.simple_change, 2),
        ('time_sel', 'pgsql.queries.test',
            'время (select)', 'ms', Plugin.DELTA.simple_change, 2),

        ('callsf', 'pgsql.queries.test',
            'число запросов (f)', 'n/m', Plugin.DELTA.as_is, 1),
        ('callsi_s', 'pgsql.queries.test',
            'число запросов (i)',   'n/m', Plugin.DELTA.as_is, 1),

        ('timef', 'pgsql.queries.test',
            'время (f)', 'ms', Plugin.DELTA.as_is, 2),
        ('timei_s', 'pgsql.queries.test',
            'время (i)',   'ms', Plugin.DELTA.as_is, 2),
    ]
    # name, type, ('graph item', color, yaxisside, drawtype)
    #   0     1         2.0        2.1     2.2       2.3
    Graphs = [
        ('test активность (calls)', 0, (
            ('calls_upd',       'CCFFCC', 1, 5),
            ('calls_sel',       'CCFFFF', 1, 5),
            ('calls_upd_Yprev', '009900', 1, 2),
            ('calls_sel_Yprev', '009999', 1, 2),),),
        ('test активность (time)', 0,  (
            ('time_upd',        'CCFFCC', 1, 5),
            ('time_sel',        'CCFFFF', 1, 5),
            ('time_upd_Yprev',  '009900', 1, 2),
            ('time_sel_Yprev',  '009999', 1, 2),),),
        ('test поиск (calls)', 0, (
            ('callsf',       'CCFFCC', 1, 5),
            ('callsi_s',       'CCFFFF', 0, 5),
            ('callsf_Yprev', '009900', 1, 2),
            ('callsi_s_Yprev', '009999', 0, 2),),),
        ('test поиск (time)', 0, (
            ('timef',         'CCFFCC', 1, 5),
            ('timei_s',         'CCFFFF', 0, 5),
            ('timef_Yprev',   '009900', 1, 2),
            ('timei_s_Yprev',   '009999', 0, 2),),),
    ]

    def run(self, zbx):
        # execute query on default database
        result = Pooler.query("""

        SELECT '_upd' as type,
               sum(calls) as calls,
               sum(total_time) as totaltime
        FROM pg_stat_statements
        where dbid = (
            select datid from pg_stat_database where datname = 'test')
          and left(query,8) = 'SELECT *' and query ~* '_UPDATE'

        union all

        SELECT '_sel' as type,
               sum(calls) as calls,
               sum(total_time) as totaltime
        FROM pg_stat_statements
        where dbid = (
            select datid from pg_stat_database where datname = 'test')
          and left(query,8) = 'SELECT *' and not (query ~* '_UPDATE')

        union all

        select left(
                substring(
                    function_name, strpos(function_name,'.')+1, 64),4) as type,
               count(*) as calls,
               max(extract(milliseconds from duration)) as time
        from statement_log -- таблица со статистикой
        where dt_start >= now()-'00:01:00'::interval
        group by left(
            substring(
                function_name, strpos(function_name,'.')+1, 64),4)
        order by 1

        """, 'test')
        # send a resulting value to zabbix
        for idx, item in enumerate(self.Items):
            key, zbxkey, val = item[0], item[1], 0
            for row in result:
                if key.endswith(row[0]):
                    val = row[item[5]]
                    self.Yprev[idx] = round(
                        self.Coef * float(val) + (
                            1 - self.Coef) * self.Yprev[idx], 1)
                    break
                else:
                    continue
            else:
                self.Yprev[idx] = self.Yprev[idx]/3  # исходных данных нет
            zbx.send(
                zbxkey + ('[{0}]'.format(key)), val, item[4])
            zbx.send(
                zbxkey + ('[{0}_Yprev]'.format(key)), self.Yprev[idx], item[4])

    # Declare zabbix items for template
    def items(self, template):
        result = ''
        for idx, item in enumerate(self.Items):
            key, zbxkey = item[0], item[1]
            result += template.item({
                'name': 'test: {0}'.format(item[2]),
                'key': zbxkey + ('[{0}]'.format(key)),
                'units': item[3]
            })
            result += template.item({
                'name': 'test: {0}_Yprev'.format(item[2]),
                'key': zbxkey + ('[{0}_Yprev]'.format(key)),
                'units': item[3]
            })
        return result

    # Declare zabbix graphs for template
    def graphs(self, template):
        result = ''
        for name in self.Graphs:
            items = []
            for item in name[2]:
                zbxkey = 'pgsql.queries.test[{0}]'.format(item[0])
                if item[3] is None:
                    items.append({
                        'key': zbxkey,
                        'color': item[1],
                        'yaxisside': item[2]
                    })
                else:
                    items.append({
                        'key': zbxkey,
                        'color': item[1],
                        'yaxisside': item[2],
                        'drawtype': item[3]
                    })
            graph = {'name': name[0], 'items': items, 'type': name[1]}
            result += template.graph(graph)

        return result
