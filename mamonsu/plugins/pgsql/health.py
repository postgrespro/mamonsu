# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler
import time


class PgHealth(Plugin):

    DEFAULT_CONFIG = {'uptime': str(60 * 10), 'cache': str(80)}

    def run(self, zbx):

        start_time = time.time()
        Pooler.query('select 1')
        zbx.send('pgsql.ping[]', (time.time() - start_time) * 100)

        result = Pooler.query("select \
            date_part('epoch', now() - pg_postmaster_start_time())")
        zbx.send('pgsql.uptime[]', int(result[0][0]))

        result = Pooler.query('select \
            round(sum(blks_hit)*100/sum(blks_hit+blks_read), 2) \
            from pg_catalog.pg_stat_database')
        zbx.send('pgsql.cache[hit]', int(result[0][0]))

    def items(self, template):
        result = template.item({
            'name': 'PostgreSQL: ping',
            'key': 'pgsql.ping[]',
            'value_type': Plugin.VALUE_TYPE.numeric_float,
            'units': Plugin.UNITS.ms
        }) + template.item({
            'name': 'PostgreSQL: service uptime',
            'key': 'pgsql.uptime[]',
            'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
            'units': Plugin.UNITS.uptime
        }) + template.item({
            'name': 'PostgreSQL: cache hit ratio',
            'key': 'pgsql.cache[hit]',
            'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
            'units': Plugin.UNITS.percent
        })
        return result

    def graphs(self, template):
        items = [
            {'key': 'pgsql.cache[hit]'},
            {'key': 'pgsql.uptime[]', 'color': 'DF0101', 'yaxisside': 1}
        ]
        graph = {'name': 'PostgreSQL uptime', 'items': items}
        return template.graph(graph)

    def triggers(self, template):
        result = template.trigger({
            'name': 'PostgreSQL service was restarted on '
            '{HOSTNAME} (uptime={ITEM.LASTVALUE})',
            'expression': '{#TEMPLATE:pgsql.uptime[].last'
            '()}&lt;' + str(self.plugin_config('uptime'))
        }) + template.trigger({
            'name': 'PostgreSQL cache hit ratio too low on '
            '{HOSTNAME} ({ITEM.LASTVALUE})',
            'expression': '{#TEMPLATE:pgsql.cache[hit].last'
            '()}&lt;' + str(self.plugin_config('cache'))
        })
        return result
