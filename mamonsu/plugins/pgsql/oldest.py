# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class Oldest(Plugin):

    OldestXidSql = """
select
    greatest(max(age(backend_xmin)), max(age(backend_xid)))
from pg_catalog.pg_stat_activity;
"""

    OldestQuerySql = """
select
    extract(epoch from max(now() - xact_start))
from pg_catalog.pg_stat_activity;
"""

    DEFAULT_CONFIG = {
        'max_xid_age': str(5000 * 60 * 60),
        'max_query_time': str(5 * 60 * 60)
    }

    def run(self, zbx):
        xid = Pooler.query(self.OldestXidSql)[0][0]
        zbx.send('pgsql.oldest[xid_age]', xid)
        query = Pooler.query(self.OldestQuerySql)[0][0]
        zbx.send('pgsql.oldest[query_time]', query)

    def graphs(self, template):
        result = template.graph({
            'name': 'PostgreSQL oldest query running time',
            'items': [{
                'key': 'pgsql.oldest[query_time]',
                'color': '00CC00'
            }]
        })
        result += template.graph({
            'name': 'PostgreSQL age of oldest xid',
            'items': [{
                'key': 'pgsql.oldest[xid_age]',
                'color': '00CC00'
            }]
        })
        return result

    def items(self, template):
        return template.item({
            'key': 'pgsql.oldest[xid_age]',
            'name': 'PostgreSQL: age of oldest xid',
            'value_type': Plugin.VALUE_TYPE.numeric_unsigned
        }) + template.item({
            'key': 'pgsql.oldest[query_time]',
            'name': 'PostgreSQL: oldest query running time in sec',
            'units': Plugin.UNITS.s
        })

    def triggers(self, template):
        return template.trigger({
            'name': 'PostgreSQL oldest xid is too big on {HOSTNAME}',
            'expression': '{#TEMPLATE:pgsql.oldest[xid_age]'
            '.last()}&gt;' + self.plugin_config('max_xid_age')
        }) + template.trigger({
            'name': 'PostgreSQL query running is too old on {HOSTNAME}',
            'expression': '{#TEMPLATE:pgsql.oldest[query_time]'
            '.last()}&gt;' + self.plugin_config('max_query_time')
        })
