# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate


class Connections(Plugin):
    AgentPluginType = "pg"
    # key: (macro, value)
    plugin_macros = {
        "connections_percent": [("macro", "{$CONNECTIONS_PERCENT}"), ("value", 90)]
    }
    # (state, key, name, graph item color)
    Items = [
        ("active", "active", "Number of Active User Connections", "00CC00"),
        ("idle", "idle", "Number of Idle User Connections", "A39B98"),
        ("idle in transaction", "idle_in_transaction",
         "Number of Idle in Transaction User Connections", "9C8A4E"),
        ("idle in transaction (aborted)", "idle_in_transaction_aborted",
         "Number of Idle in Transaction (Aborted) User Connections", "F6CB93"),
        ("fastpath function call", "fastpath_function_call",
         "Number of Fastpath Function Call User Connections", "00B0B8"),
        ("disabled", "disabled",
         "Number of Disabled User Connections",
         "3B415A")
    ]

    # for PG 10+
    default_backend_types = ["archiver", "autovacuum launcher", "autovacuum worker", "background worker",
                             "background writer", "client backend", "checkpointer", "logical replication launcher",
                             "logical replication worker", "parallel worker", "startup", "walreceiver", "walsender",
                             "walwriter"]
    query_other_connections = """
    SELECT coalesce(count(*), 0)
       FROM pg_catalog.pg_stat_activity
       WHERE (backend_type NOT IN ('{0}'));
    """.format("', '".join(default_backend_types))

    query_agent = """
    SELECT count(*)
    FROM pg_catalog.pg_stat_activity
    WHERE state = '{0}' {1};
    """
    query_agent_total = """
    SELECT count(*)
    FROM pg_catalog.pg_stat_activity
    WHERE {0};
    """
    query_agent_waiting_new_v = """
    SELECT count(*)
    FROM pg_catalog.pg_stat_activity
    WHERE {0}
    AND wait_event_type IS NOT NULL;
    """
    query_agent_waiting_old_v = """
    SELECT count(*)
    FROM pg_catalog.pg_stat_activity
    WHERE waiting
    AND {0};
    """
    query_agent_max_conn = """
    SELECT setting::int
    FROM pg_settings
    WHERE name = 'max_connections';
    """
    key = "pgsql.connections{0}"
    graph_name = "PostgreSQL Connections: Overview"

    def run(self, zbx):
        if Pooler.is_bootstraped() and Pooler.bootstrap_version_greater("2.3.4"):
            result = Pooler.query("""
            SELECT state,
                   count(*)
            FROM mamonsu.get_connections_states()
            GROUP BY state;
            """)
        else:
            result = Pooler.query("""
            SELECT state,
                   count(*)
            FROM pg_catalog.pg_stat_activity
            WHERE {0}
            GROUP BY state;
            """.format(
                "(backend_type = 'client backend' OR backend_type = 'parallel worker')" if Pooler.server_version_greater(
                    "10.0") else "state IS NOT NULL"))

        for item in self.Items:
            state, key, value = item[0], item[1], 0
            for row in result:
                if row[0] != state:
                    continue
                else:
                    value = row[1]
                    break
            zbx.send("pgsql.connections[{0}]".format(key), float(value))

        total = (sum([int(count) for state, count in result if state is not None]))
        zbx.send("pgsql.connections[total]", total)

        if Pooler.is_bootstraped() and Pooler.bootstrap_version_greater("2.3.4"):
            result = Pooler.query("""
            SELECT count(*)
            FROM mamonsu.get_connections_states()
            WHERE waiting IS NOT NULL;
            """)
        else:
            if Pooler.server_version_less("9.5.0"):
                result = Pooler.query("""
                SELECT count(*)
                FROM pg_catalog.pg_stat_activity
                WHERE waiting
                AND state IS NOT NULL;
                """)
            else:
                result = Pooler.query("""
                SELECT count(*)
                FROM pg_catalog.pg_stat_activity
                WHERE {0}
                AND wait_event_type IS NOT NULL;
                """.format(
                    "(backend_type = 'client backend' OR backend_type = 'parallel worker')" if Pooler.server_version_greater(
                        "10.0") else "state IS NOT NULL"))
        zbx.send("pgsql.connections[waiting]", int(result[0][0]))

        result = Pooler.query("""
        SELECT setting
        FROM pg_settings
        WHERE name = 'max_connections';
        """)
        zbx.send("pgsql.connections[max_connections]", int(result[0][0]))

        if Pooler.server_version_greater("10.0"):
            result = Pooler.query(self.query_other_connections)
            zbx.send("pgsql.connections[other]", int(result[0][0]))

    def items(self, template, dashboard=False):
        result = template.item({
            "name": "PostgreSQL Connections: Number of Total User Connections",
            "key": self.right_type(self.key, "total"),
            "delay": self.plugin_config("interval")
        })
        result += template.item({
            "name": "PostgreSQL Connections: Number of Waiting User Connections",
            "key": self.right_type(self.key, "waiting"),
            "delay": self.plugin_config("interval")
        })
        result += template.item({
            "name": "PostgreSQL Connections: Max Connections",
            "key": self.right_type(self.key, "max_connections"),
            "delay": self.plugin_config("interval")
        })

        for item in self.Items:
            result += template.item({
                "name": "PostgreSQL Connections: {0}".format(item[2]),
                "key": self.right_type(self.key, item[1]),
                "delay": self.plugin_config("interval")
            })

        if Pooler.server_version_greater("10.0"):
            result += template.item({
                "name": "PostgreSQL Connections: Number of Other Connections",
                "key": self.right_type(self.key, "other"),
                "delay": self.plugin_config("interval")
            })

        if not dashboard:
            return result
        else:
            return []

    def graphs(self, template, dashboard=False):
        items = []
        for item in self.Items:
            items.append({
                "key": self.right_type(self.key, item[1]),
                "color": item[3],
                "drawtype": 2
            })
        items.append({
            "key": self.right_type(self.key, "total"),
            "color": "FF5656",
            "drawtype": 2
        })
        items.append({
            "key": self.right_type(self.key, "waiting"),
            "color": "006AAE",
            "drawtype": 2
        })

        if Pooler.server_version_greater("10.0"):
            items.append({
                "key": self.right_type(self.key, "other"),
                "color": "87C2B9",
                "drawtype": 2
            })

        graph = {
            "name": self.graph_name,
            "type": 1,
            "items": items
        }

        if not dashboard:
            return template.graph(graph)
        else:
            return [{
                "dashboard": {"name": graph["name"],
                              "page": ZbxTemplate.dashboard_page_overview["name"],
                              "size": ZbxTemplate.dashboard_widget_size_medium,
                              "position": 1}
            }]

    def macros(self, template, dashboard=False):
        result = ""
        for macro in self.plugin_macros.keys():
            result += template.mamonsu_macro(defaults=self.plugin_macros[macro])
        if not dashboard:
            return result
        else:
            return []

    def triggers(self, template, dashboard=False):
        return template.trigger({
            "name": "PostgreSQL Connections: too many connections on {HOSTNAME} (total connections more than " +
                    self.plugin_macros["connections_percent"][0][1] + "% of max_connections)",
            "expression": " {#TEMPLATE:" + self.right_type(self.key,
                                                           "total") + ".last()}/{#TEMPLATE:" + self.right_type(self.key,
                                                                                                               "max_connections") + ".last()}*100 >" +
                          self.plugin_macros["connections_percent"][0][1]
        })

    def keys_and_queries(self, template_zabbix):
        result = []
        for item in self.Items:
            result.append("{0}[*],$2 $1 -c \"{1}\"".format(self.key.format("." + item[1]),
                                                              self.query_agent.format(item[1],
                                                                                      "AND (backend_type = 'client backend' OR backend_type = 'parallel worker')" if Pooler.server_version_greater("10") else "")))
        result.append("{0}[*],$2 $1 -c \"{1}\"".format(self.key.format(".total"), self.query_agent_total.format(
            "(backend_type = 'client backend' OR backend_type = 'parallel worker')" if Pooler.server_version_greater("10") else "state IS NOT NULL")))
        if Pooler.server_version_less("9.5"):
            result.append(
                "{0}[*],$2 $1 -c \"{1}\"".format(self.key.format(".waiting"), self.query_agent_waiting_old_v.format(
                    "(backend_type = 'client backend' OR backend_type = 'parallel worker')" if Pooler.server_version_greater("10") else "state IS NOT NULL")))
        else:
            result.append(
                "{0}[*],$2 $1 -c \"{1}\"".format(self.key.format(".waiting"), self.query_agent_waiting_new_v.format(
                    "(backend_type = 'client backend' OR backend_type = 'parallel worker')" if Pooler.server_version_greater("10") else "state IS NOT NULL")))
            if Pooler.server_version_greater("10"):
                result.append("{0}[*],$2 $1 -c \"{1}\"".format(self.key.format(".other"),
                                                                  self.query_other_connections.format(
                                                                      "', '".join(self.default_backend_types))))
        result.append(
            "{0}[*],$2 $1 -c \"{1}\"".format(self.key.format(".max_connections"), self.query_agent_max_conn))
        return template_zabbix.key_and_query(result)
