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
         "Read only queries",
         "0000CC"),
        ("rowshare",
         "SELECT FOR SHARE and SELECT FOR UPDATE",
         "00CC00"),
        ("rowexclusive",
         "Write queries",
         "CC0000"),
        ("shareupdateexclusive",
         "VACUUM, ANALYZE, CREATE INDEX CONCURRENTLY",
         "CC00CC"),
        ("share",
         "CREATE INDEX",
         "777777"),
        ("sharerowexclusive",
         "Locks from application",
         "CCCCCC"),
        ("exclusive",
         "Locks from application or some operation on system catalogs",
         "CCCC00"),
        ("accessexclusive",
         "ALTER TABLE, DROP TABLE, TRUNCATE, REINDEX, CLUSTER, VACUUM FULL, LOCK TABLE",
         "00CCCC")
    ]

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
                "name": "PostgreSQL locks: {0}".format(item[1]),
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
        name, items = "PostgreSQL locks sampling", []
        for item in self.Items:
            items.append({
                "key": self.right_type(self.key, item[0]),
                "color": item[2]
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
