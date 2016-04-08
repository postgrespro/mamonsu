# -*- coding: utf-8 -*-

from mamonsu.lib.plugin import Plugin
from mamonsu.plugins.pgsql.pool import Pooler


# Count all queries running more then 5 minutes
class ExamplePlugin(Plugin):

    # execute method run() every 60s
    Interval = 60

    def run(self, zbx):
        # execute query on default database
        result = Pooler.query("""
            select
                count(*)
            from pg_catalog.pg_stat_activity
                where
                    state <> 'idle' and
                    now() - pg_stat_activity.query_start > interval '5 minutes'
        """)
        # send a resulting value to zabbix
        zbx.send('pgsql.queries.long_count[]', result[0][0])
        # debug message
        self.log.debug('some information for debug')

    # Declare zabbix items for template
    def items(self, template):
        return template.item({
            'name': 'Count of long running queries',
            'key': 'pgsql.queries.long_count[]'
        })

    # Declare zabbix graphs for template
    def graphs(self, template):
        items = [
            {
                'key': 'pgsql.queries.long_count[]',
                'color': 'DF0101',
                'yaxisside': 0
            }
        ]
        graph = {'name': 'PostgreSQL long running queries', 'items': items}
        return template.graph(graph)

    # Declare zabbix trigger for template
    def triggers(self, template):
        return template.trigger({
            'name': "Long running queries ({HOSTNAME}: {ITEM.LASTVALUE})",
            'expression': "{#TEMPLATE:pgsql.queries.long_count[].last()}&lt;10"
        })
