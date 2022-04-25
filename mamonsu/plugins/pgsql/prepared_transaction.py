# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate


class PreparedTransaction(Plugin):
    key_count = {
        "state": "count_prepared",
        "key": "pgsql.prepared.count",
        "name": "PostgreSQL Prepared Transactions: Number of Prepared Transactions",
        "color": "8B817C",
        "yaxisside": 0,
    }
    key_prepared = {
        "state": "oldest_prepared",
        "key": "pgsql.prepared.oldest",
        "name": "PostgreSQL Prepared Transactions: the Oldest Prepared Transaction Running Time in sec",
        "color": "9C8A4E",
        "yaxisside": 1,
    }
    query_prepared = """
    SELECT COUNT(*) AS count_prepared,
           coalesce(ROUND(MAX(EXTRACT (EPOCH FROM (now() - prepared)))),0)::bigint AS oldest_prepared
    FROM pg_catalog.pg_prepared_xacts;
    """
    query_prepared_bootstraped = """
    SELECT *
    FROM mamonsu.prepared_transaction();
    """

    DEFAULT_CONFIG = {
        "max_prepared_transaction_time": str(5 * 60 * 60)
    }

    def run(self, zbx):
        if Pooler.is_bootstraped():
            result = Pooler.query(self.query_prepared_bootstraped)
        else:
            result = Pooler.query(self.query_prepared)

        for count_prepared, oldest_prepared in result:
            zbx.send(self.key_count["key"], count_prepared)
            zbx.send(self.key_prepared["key"], oldest_prepared)

    def items(self, template, dashboard=False):
        result = template.item({
            "name": self.key_count["name"],
            "key": self.key_count["key"],
        })
        result += template.item({
            "name": self.key_prepared["name"],
            "key": self.key_prepared["key"],
            "delay": self.plugin_config("interval")
        })
        if not dashboard:
            return result
        else:
            return [{
                "dashboard": {"name": self.key_count["key"],
                              "page": ZbxTemplate.dashboard_page_transactions["name"],
                              "size": ZbxTemplate.dashboard_widget_size_medium,
                              "position": 3}
            },
                {
                    "dashboard": {"name": self.key_prepared["key"],
                                  "page": ZbxTemplate.dashboard_page_transactions["name"],
                                  "size": ZbxTemplate.dashboard_widget_size_medium,
                                  "position": 4}
                }]

    def graphs(self, template, dashboard=False):
        result = template.graph({
            "name": "PostgreSQL Prepared Transactions: Overview",
            "items": [{
                "key": self.key_count["key"],
                "color": self.key_count["color"],
                "yaxisside": self.key_count["yaxisside"],
                "drawtype": 2
            },
                {
                    "key": self.key_prepared["key"],
                    "color": self.key_prepared["color"],
                    "yaxisside": self.key_prepared["yaxisside"],
                    "drawtype": 2
                },
            ]
        })
        if not dashboard:
            return result
        else:
            return []

    def triggers(self, template, dashboard=False):
        result = template.trigger({
            "name": "PostgreSQL prepared transaction is too old on {HOSTNAME}",
            "expression": "{#TEMPLATE:" + self.key_prepared["key"] + ".last()}&gt;" + self.plugin_config(
                "max_prepared_transaction_time")
        })
        return result
