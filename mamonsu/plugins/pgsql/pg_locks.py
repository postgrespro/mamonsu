# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate


class PgLocks(Plugin):
    AgentPluginType = "pg"
    query = """
    SELECT lower(mode),
           count(mode)
    FROM pg_catalog.pg_locks 
    GROUP BY 1;
    """
    query_agent = """
    SELECT count(*)
    FROM pg_catalog.pg_locks
    WHERE lower(mode)='{0}';
    """
    key = "pgsql.pg_locks{0}"
    Items = [
        # key, desc, color
        ("accessshare",
         "total number of locks acquired (or waiting) by queries that only reads tables and do not modify",
         "00CC00"),
        ("rowshare",
         "total number of locks acquired (or waiting) by all queries like SELECT FOR SHARE and SELECT FOR UPDATE",
         "3B415A"),
        ("rowexclusive",
         "total number of locks acquired (or waiting) by all queries like UPDATE, DELETE, INSERT and MERGE",
         "FF5656"),
        ("shareupdateexclusive",
         "total number of locks acquired (or waiting) by all queries like VACUUM, ANALYZE, CREATE INDEX CONCURRENTLY, CREATE STATISTICS, COMMENT ON, REINDEX CONCURRENTLY, and some forms of ALTER INDEX and ALTER TABLE",
         "F6CB93"),
        ("share",
         "total number of locks acquired (or waiting) by all queries like CREATE INDEX",
         "006AAE"),
        ("sharerowexclusive",
         "total number of locks acquired (or waiting) by all queries like CREATE TRIGGER and some forms of ALTER TABLE",
         "00B0B8"),
        ("exclusive",
         "total number of locks acquired (or waiting) by all queries like REFRESH MATERIALIZED VIEW CONCURRENTLY",
         "9C8A4E"),
        ("accessexclusive",
         "total number of locks acquired (or waiting) by all queries like DROP TABLE, TRUNCATE, REINDEX, CLUSTER, VACUUM FULL, REFRESH MATERIALIZED VIEW, LOCK TABLE and some forms of ALTER INDEX and ALTER TABLE",
         "793F5D")
    ]

    graph_name = "PostgreSQL: Locks Sampling"

    def run(self, zbx):
        result = Pooler.query(self.query)
        for item in self.Items:
            found = False
            for row in result:
                if row[0] == "{0}lock".format(item[0]):
                    found = True
                    zbx.send("pgsql.pg_locks[{0}]".format(item[0]), row[1])
            if not found:
                zbx.send("pgsql.pg_locks[{0}]".format(item[0]), 0)

    def items(self, template, dashboard=False):
        result = ""
        for item in self.Items:
            result += template.item({
                "key": self.right_type(self.key, item[0]),
                "name": "PostgreSQL Locks: {0}".format(item[1]),
                "delay": self.plugin_config("interval"),
                "value_type": self.VALUE_TYPE.numeric_unsigned
            })
        if not dashboard:
            return result
        else:
            lock_graphs = []
            for index, item in enumerate(self.Items):
                lock_graphs.append({
                    "dashboard": {"name": self.right_type(self.key, item[0]),
                                  "page": ZbxTemplate.dashboard_page_locks["name"],
                                  "size": ZbxTemplate.dashboard_widget_size_small,
                                  "position": index + 2}
                })
            return lock_graphs

    def graphs(self, template, dashboard=False):
        name = self.graph_name
        items = []
        for item in self.Items:
            items.append({
                "key": self.right_type(self.key, item[0]),
                "color": item[2],
                "drawtype": 2
            })
        if not dashboard:
            return template.graph({
                "name": name,
                "items": items
            })
        else:
            return []

    def keys_and_queries(self, template_zabbix):
        result = []
        for item in self.Items:
            result.append("{0}[*],$2 $1 -c \"{1}\"".format(self.key.format("." + item[0]),
                                                              self.query_agent.format("{0}lock".format(item[0]))))
        return template_zabbix.key_and_query(result)
