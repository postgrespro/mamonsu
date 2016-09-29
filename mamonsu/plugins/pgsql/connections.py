# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class Connections(Plugin):

    # (state, key, name, graph)
    Items = [
        ('active', 'active', 'number of active connections', '00BB00'),
        ('idle', 'idle', 'number of idle connections', '0000BB'),
        ('idle in transaction', 'idle_in_transaction',
            'number of idle in transaction connections', 'CC00CC')
    ]

    def run(self, zbx):

        result = Pooler.query('select state, count(*) \
            from pg_catalog.pg_stat_activity group by state')
        for item in self.Items:
            state, key, val = item[0], item[1], 0
            for row in result:
                if row[0] != state:
                    continue
                else:
                    val = row[1]
                    break
            zbx.send('pgsql.connections[{0}]'.format(key), float(val))

        result = Pooler.query('select count(*) \
            from pg_catalog.pg_stat_activity')
        zbx.send('pgsql.connections[total]', int(result[0][0]))

        if Pooler.server_version_less('9.5.0'):
            result = Pooler.query('select count(*) \
                from pg_catalog.pg_stat_activity where waiting')
            zbx.send('pgsql.connections[waiting]', int(result[0][0]))

    def items(self, template):
        result = template.item({
            'name': 'PostgreSQL: number of total connections',
            'key': 'pgsql.connections[total]'
        })
        result += template.item({
            'name': 'PostgreSQL: number of waiting connections',
            'key': 'pgsql.connections[waiting]'
        })
        for item in self.Items:
            result += template.item({
                'name': 'PostgreSQL: {0}'.format(item[2]),
                'key': 'pgsql.connections[{0}]'.format(item[1])
            })
        return result

    def graphs(self, template):
        items = []
        for item in self.Items:
            items.append({
                'key': 'pgsql.connections[{0}]'.format(item[1]),
                'color': item[3]
            })
        items.append({
            'key': 'pgsql.connections[total]',
            'color': 'EEEEEE'
        })
        items.append({
            'key': 'pgsql.connections[waiting]',
            'color': 'BB0000'
        })
        graph = {'name': 'PostgreSQL connections', 'items': items}
        return template.graph(graph)
