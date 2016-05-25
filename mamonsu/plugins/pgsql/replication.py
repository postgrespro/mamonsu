# -*- coding: utf-8 -*-

from mamonsu.lib.plugin import Plugin
from .pool import Pooler


class Replication(Plugin):

    TriggerLagMoreThen = 360

    def run(self, zbx):
        # recovery
        result = Pooler.query('select pg_is_in_recovery()')
        if result[0][0] == 't':
            lag = Pooler.query('select extract(epoch from now() \
                - pg_last_xact_replay_timestamp())')
            zbx.send('pgsql.replication_lag[sec]', lag[0][0])
        # xlog location
        result = Pooler.query("select \
            pg_xlog_location_diff(pg_current_xlog_location(),'0/00000000')")
        zbx.send('pgsql.wal.write[]', result[0][0])

    def items(self, template):
        return template.item({
            'name': 'PostgreSQL: streaming replication lag in seconds',
            'key': 'pgsql.replication_lag[sec]'
        }) + template.item({
            'name': 'PostgreSQL: wal write speed',
            'key': 'pgsql.wal.write[]',
            'units': 'b',
            'delta': 2
        })

    def graphs(self, template):
        items = [
            {'color': '00CC00',
                'key': 'pgsql.wal.write[]'},
            {'color': 'CC0000',
                'key': 'pgsql.replication_lag[sec]',
                'yaxisside': 1}
        ]
        graph = {'name': 'PostgreSQL streaming lag', 'items': items}
        return template.graph(graph)

    def triggers(self, template):
        return template.trigger({
            'name': 'PostgreSQL streaming lag to high '
            'on {HOSTNAME} (value={ITEM.LASTVALUE})',
            'expression': '{#TEMPLATE:pgsql.replication_lag[sec].last'
            '()}&gt;' + str(self.TriggerLagMoreThen)
        })
