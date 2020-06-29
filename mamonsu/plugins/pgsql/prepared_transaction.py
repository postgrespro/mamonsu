# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler


class PreparedTransaction(Plugin):
    Interval = 6
    key_count = {
        'state': 'count_prepared',
        'key': 'pgsql.prepared.count',
        'name': 'PostgreSQL: number of prepared transactions',
        'color': '00BB00',
        'yaxisside': 0,
    }
    key_prepared = {
        'state': 'oldest_prepared',
        'key': 'pgsql.prepared.oldest',
        'name': 'PostgreSQL: oldest prepared transaction running time in sec',
        'color': '0000BB',
        'yaxisside': 1,
    }
    query_prepared = "SELECT COUNT(*) as count_prepared, " \
                     "coalesce (ROUND(MAX(EXTRACT (EPOCH FROM (now() - prepared)))),0)::bigint " \
                     "AS oldest_prepared  FROM pg_catalog.pg_prepared_xacts"
    query_prepared_bootstraped = "SELECT * FROM public.mamonsu_prepared_transaction()"

    DEFAULT_CONFIG = {
        'max_prepared_transaction_time': str(5 * 60 * 60)
    }

    def run(self, zbx):
        if Pooler.is_bootstraped():
            result = Pooler.query(self.query_prepared_bootstraped)
        else:
            result = Pooler.query(self.query_prepared)

        for count_prepared, oldest_prepared in result:
            zbx.send(self.key_count['key'], count_prepared)
            zbx.send(self.key_prepared['key'], oldest_prepared)

    def items(self, template):
        result = template.item({
            'name': self.key_count['name'],
            'key': self.key_count['key'],
        })
        result += template.item({
            'name': self.key_prepared['name'],
            'key': self.key_prepared['key'],
            'delay': self.plugin_config('interval')
        })

        return result

    def graphs(self, template):
        result = template.graph({
            'name': 'PostgreSQL prepared transaction',
            'items': [{
                'key': self.key_count['key'],
                'color': self.key_count['color'],
                'yaxisside': self.key_count['yaxisside'],
            },
                {
                    'key': self.key_prepared['key'],
                    'color': self.key_prepared['color'],
                    'yaxisside': self.key_prepared['yaxisside'],
                },
            ]
        })
        return result

    def triggers(self, template):
        result = template.trigger({
            'name': 'PostgreSQL prepared transaction running is too old on {HOSTNAME}',
            'expression': '{#TEMPLATE:' + self.key_prepared['key'] +
                          '.last()}&gt;' + self.plugin_config('max_prepared_transaction_time')
        })
        return result

