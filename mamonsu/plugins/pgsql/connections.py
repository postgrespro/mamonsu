# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from distutils.version import LooseVersion
from .pool import Pooler


class Connections(Plugin):
    AgentPluginType = 'pg'
    # (state, key, name, graph)
    Items = [
        ('active', 'active', 'number of active connections', '00BB00'),
        ('idle', 'idle', 'number of idle connections', '0000BB'),
        ('idle in transaction', 'idle_in_transaction',
         'number of idle in transaction connections', 'CC00CC')
    ]
    query_agent = "select count(*) from pg_catalog.pg_stat_activity where state = '{0}';"
    query_agent_total = "select count(*) from pg_catalog.pg_stat_activity where state is not null ;"
    query_agent_waiting_new_v = "select count(*) from pg_catalog.pg_stat_activity where state is not null and " \
                                " wait_event_type is not null"
    query_agent_waiting_old_v = "select count(*) from pg_catalog.pg_stat_activity where waiting and state is not null "
    key = 'pgsql.connections{0}'

    def run(self, zbx):

        if Pooler.is_bootstraped() and Pooler.bootstrap_version_greater('2.3.4'):
            result = Pooler.query(
                'select state, count(*) '
                'from mamonsu_get_connections_states() where state is not null group by state')
        else:
            result = Pooler.query(
                'select state, count(*) '
                'from pg_catalog.pg_stat_activity where state is not null group by state')

        for item in self.Items:
            state, key, val = item[0], item[1], 0
            for row in result:
                if row[0] != state:
                    continue
                else:
                    val = row[1]
                    break
            zbx.send('pgsql.connections[{0}]'.format(key), float(val))

        total = (sum([int(count) for state, count in result if state is not None]))
        zbx.send('pgsql.connections[total]', total)

        if Pooler.is_bootstraped() and Pooler.bootstrap_version_greater('2.3.4'):
            result = Pooler.query(
                'select count(*) '
                'from mamonsu_get_connections_states() '
                'where waiting and state is not null')
        else:
            if Pooler.server_version_less('9.5.0'):
                result = Pooler.query(
                    'select count(*) '
                    'from pg_catalog.pg_stat_activity where waiting and state is not null')
            else:
                result = Pooler.query('select count(*) from pg_catalog.pg_stat_activity where state is not null and '
                                      'wait_event_type is not null')
        zbx.send('pgsql.connections[waiting]', int(result[0][0]))

    def items(self, template):
        result = template.item({
            'name': 'PostgreSQL: number of total connections',
            'key': self.right_type(self.key, "total")
        })
        result += template.item({
            'name': 'PostgreSQL: number of waiting connections',
            'key': self.right_type(self.key, "waiting")
        })
        for item in self.Items:
            result += template.item({
                'name': 'PostgreSQL: {0}'.format(item[2]),
                'key': self.right_type(self.key, item[1])
            })
        return result

    def graphs(self, template):
        items = []
        for item in self.Items:
            items.append({
                'key': self.right_type(self.key, item[1]),
                'color': item[3]
            })
        items.append({
            'key': self.right_type(self.key, "total"),
            'color': 'EEEEEE'
        })
        items.append({
            'key': self.right_type(self.key, "waiting"),
            'color': 'BB0000'
        })
        graph = {'name': 'PostgreSQL connections', 'items': items}
        return template.graph(graph)

    def keys_and_queries(self, template_zabbix):
        result = []
        for item in self.Items:
            result.append(
                '{0}[*],$2 $1 -c "{1}"'.format(self.key.format("." + item[1]), self.query_agent.format(item[1])))
        result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key.format('.total'), self.query_agent_total))
        if self.VersionPG['number'] < LooseVersion('9.6'):
            result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key.format('.waiting'), self.query_agent_waiting_old_v))
        else:
            result.append('{0}[*],$2 $1 -c "{1}"'.format(self.key.format('.waiting'), self.query_agent_waiting_new_v))
        return template_zabbix.key_and_query(result)

    def sql(self):
        result = {}  # key is name of file, var is query
        for item in self.Items:
            result[self.key.format("." + item[1])] = self.query_agent.format(item[1])
        result[self.key.format('.total')] = self.query_agent_total
        if self.VersionPG['number'] < LooseVersion('9.6'):
            result[self.key.format('.waiting')] = self.query_agent_waiting_old_v
        else:
            result[self.key.format('.waiting')] = self.query_agent_waiting_new_v
        return result
