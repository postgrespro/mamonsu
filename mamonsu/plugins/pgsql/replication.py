# -*- coding: utf-8 -*-

from mamonsu.lib.plugin import Plugin
from .pool import Pooler


class Replication(Plugin):

    TriggerLagMoreThen = 360

    def run(self, zbx):
        result = Pooler.query('select pg_is_in_recovery()')
        print("result[0][0] {0}".format(result[0][0]))
        if result[0][0] == 't':
            lag = Pooler.query('select extract(epoch from now() \
                - pg_last_xact_replay_timestamp())')
            zbx.send('pgsql.replication_lag[sec]', lag[0][0])

    def items(self, template):
        return template.item({
            'name': 'PostgreSQL: streaming replication lag in seconds',
            'key': 'pgsql.replication_lag[sec]'
        })

    def graphs(self, template):
        items = [{'key': 'pgsql.replication_lag[sec]'}]
        graph = {'name': 'PostgreSQL streaming lag', 'items': items}
        return template.graph(graph)

    def triggers(self, template):
        return template.trigger({
            'name': 'PostgreSQL streaming lag to high '
            'on {HOSTNAME} (value={ITEM.LASTVALUE})',
            'expression': '{#TEMPLATE:pgsql.replication_lag[sec].last'
            '()}&gt;' + str(self.TriggerLagMoreThen)
        })
