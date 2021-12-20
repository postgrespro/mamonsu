# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate


class Oldest(Plugin):
    AgentPluginType = "pg"
    key = "pgsql.oldest{0}"
    OldestXidSql = """
    SELECT greatest(max(age(backend_xmin)),
           max(age(backend_xid)))
    FROM pg_catalog.pg_stat_activity;
    """
    OldestXidSql_bootstrap = """
    SELECT mamonsu.get_oldest_xid();
    """
    OldestTransactionSql = """
    SELECT
        CASE WHEN extract(epoch from max(now() - xact_start)) IS NOT NULL AND extract(epoch FROM max(now() - xact_start))>0
             THEN extract(epoch from max(now() - xact_start))
             ELSE 0
        END
    FROM pg_catalog.pg_stat_activity
    WHERE pid NOT IN (SELECT pid FROM pg_stat_replication)
    AND pid <> pg_backend_pid();
    """
    OldestTransactionSql_bootstrap = """
    SELECT mamonsu.get_oldest_transaction();
    """
    ParallelQueries = """
    SELECT count(*)
    FROM pg_stat_activity
    WHERE leader_pid is not NULL;
    """

    DEFAULT_CONFIG = {
        "max_xid_age": str(5000 * 60 * 60),
        "max_transaction_time": str(5 * 60 * 60)
    }

    def run(self, zbx):
        if Pooler.is_bootstraped() and Pooler.bootstrap_version_greater("2.3.2"):
            xid = Pooler.query(self.OldestXidSql_bootstrap)[0][0]
            query = Pooler.query(self.OldestTransactionSql_bootstrap)[0][0]
        else:
            xid = Pooler.query(self.OldestXidSql)[0][0]
            query = Pooler.query(self.OldestTransactionSql)[0][0]
        if Pooler.server_version_greater("13"):
            parallel_queries = Pooler.query(self.ParallelQueries)[0][0]
            zbx.send("pgsql.parallel[queries]", parallel_queries)
        zbx.send("pgsql.oldest[xid_age]", xid)
        zbx.send("pgsql.oldest[transaction_time]", query)

    def items(self, template, dashboard=False):
        if not dashboard:
            return template.item({
                "key": self.right_type(self.key, "xid_age"),
                "name": "PostgreSQL: age of oldest xid",
                "delay": self.plugin_config("interval"),
                "value_type": Plugin.VALUE_TYPE.numeric_unsigned
            }) + template.item({
                "key": self.right_type(self.key, "transaction_time"),
                "name": "PostgreSQL: oldest transaction running time in sec",
                "delay": self.plugin_config("interval"),
                "units": Plugin.UNITS.s
            }) + template.item({
                "key": self.right_type("pgsql.parallel{0}", "queries"),
                "name": "PostgreSQL: number of parallel queries being executed now",
                "delay": self.plugin_config("interval"),
                "value_type": Plugin.VALUE_TYPE.numeric_unsigned
            })
        else:
            return [{
                "dashboard": {"name": self.right_type(self.key, "xid_age"),
                              "page": ZbxTemplate.dashboard_page_transactions["name"],
                              "size": ZbxTemplate.dashboard_widget_size_medium,
                              "position": 1}
            },
                {
                    "dashboard": {"name": self.right_type(self.key, "transaction_time"),
                                  "page": ZbxTemplate.dashboard_page_transactions["name"],
                                  "size": ZbxTemplate.dashboard_widget_size_medium,
                                  "position": 2}
                }]

    def triggers(self, template, dashboard=False):
        return template.trigger({
            "name": "PostgreSQL oldest xid is too big on {HOSTNAME}",
            "expression": "{#TEMPLATE:" + self.right_type(self.key, "xid_age") + ".last()}&gt;" + self.plugin_config(
                "max_xid_age")
        }) + template.trigger({
            "name": "PostgreSQL query running is too old on {HOSTNAME}",
            "expression": "{#TEMPLATE:" + self.right_type(self.key,
                                                          "transaction_time") + ".last()}&gt;" + self.plugin_config(
                "max_transaction_time")
        })

    def keys_and_queries(self, template_zabbix):
        result = ["{0}[*],$2 $1 -c \"{1}\"".format(self.key.format(".xid_age"), self.OldestXidSql),
                  "{0}[*],$2 $1 -c \"{1}\"".format(self.key.format(".transaction_time"), self.OldestTransactionSql),
                  "{0}[*],$2 $1 -c \"{1}\"".format("pgsql.parallel{0}".format(".queries"), self.ParallelQueries)]
        return template_zabbix.key_and_query(result)
