# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from distutils.version import LooseVersion
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate


class Connections(Plugin):
    AgentPluginType = "pg"
    # (state, key, name, graph)
    DEFAULT_CONFIG = {
        "percent_connections_tr": str(90)
    }
    # (state, key, name, graph)
    Items = [
        ("active", "active", "number of active connections", "00BB00"),
        ("idle", "idle", "number of idle connections", "0000BB"),
        ("idle in transaction", "idle_in_transaction",
         "number of idle in transaction connections", "CC00CC"),
        ("idle in transaction (aborted)", "idle_in_transaction_aborted",
         "number of idle in transaction (aborted)", "CCCCCC"),
        ("fastpath function call", "fastpath_function_call",
         "number of fastpath function call", "CCCC00"),
        ("disabled", "disabled",
         "number of disabled",
         "00CCCC")
    ]

    Max_connections = None

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
        if self.Max_connections is None:
            result = Pooler.query("""
            SELECT setting
            FROM pg_settings
            WHERE name = 'max_connections';
            """)
            self.Max_connections = result[0][0]
        zbx.send("pgsql.connections[max_connections]", int(self.Max_connections))

    def items(self, template, dashboard=False):
        result = template.item({
            "name": "PostgreSQL: number of total connections",
            "key": self.right_type(self.key, "total"),
            "delay": self.plugin_config("interval")
        })
        result += template.item({
            "name": "PostgreSQL: number of waiting connections",
            "key": self.right_type(self.key, "waiting"),
            "delay": self.plugin_config("interval")
        })
        result += template.item({
            "name": "PostgreSQL: max connections",
            "key": self.right_type(self.key, "max_connections"),
            "delay": self.plugin_config("interval")
        })

        for item in self.Items:
            result += template.item({
                "name": "PostgreSQL: {0}".format(item[2]),
                "key": self.right_type(self.key, item[1]),
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
                "color": item[3]
            })
        items.append({
            "key": self.right_type(self.key, "total"),
            "color": "EEEEEE"
        })
        items.append({
            "key": self.right_type(self.key, "waiting"),
            "color": "BB0000"
        })
        items.append({
            "key": self.right_type(self.key, "max_connections"),
            "color": "00BB00"
        })
        graph = {
            "name": "PostgreSQL connections",
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

    def triggers(self, template, dashboard=False):
        return template.trigger({
            "name": "PostgreSQL many connections on {HOSTNAME} (total connections more than " + self.plugin_config(
                "percent_connections_tr") + "% max connections)",
            "expression": " {#TEMPLATE:" + self.right_type(self.key,
                                                           "total") + ".last()}/{#TEMPLATE:" + self.right_type(self.key,
                                                                                                               "max_connections") + ".last()}*100 >" + self.plugin_config(
                "percent_connections_tr")
        })

    def keys_and_queries(self, template_zabbix):
        result = []
        for item in self.Items:
            result.append("{0}[*],$2 $1 -c \"{1}\"".format(self.key.format("." + item[1]),
                                                           self.query_agent.format(item[1],
                                                                                   "AND (backend_type = 'client backend' OR backend_type = 'parallel worker')" if LooseVersion(
                                                                                       self.VersionPG) >= LooseVersion(
                                                                                       "10") else "")))
        result.append("{0}[*],$2 $1 -c \"{1}\"".format(self.key.format(".total"), self.query_agent_total.format(
            "(backend_type = 'client backend' OR backend_type = 'parallel worker')" if LooseVersion(
                self.VersionPG) >= LooseVersion(
                "10") else "state IS NOT NULL")))
        if LooseVersion(self.VersionPG) < LooseVersion("9.6"):
            result.append(
                "{0}[*],$2 $1 -c \"{1}\"".format(self.key.format(".waiting"), self.query_agent_waiting_old_v.format(
                    "(backend_type = 'client backend' OR backend_type = 'parallel worker')" if LooseVersion(
                        self.VersionPG) >= LooseVersion(
                        "10") else "state IS NOT NULL")))
        else:
            result.append(
                "{0}[*],$2 $1 -c \"{1}\"".format(self.key.format(".waiting"), self.query_agent_waiting_new_v.format(
                    "(backend_type = 'client backend' OR backend_type = 'parallel worker')" if LooseVersion(
                        self.VersionPG) >= LooseVersion(
                        "10") else "state IS NOT NULL")))
        result.append("{0}[*],$2 $1 -c \"{1}\"".format(self.key.format(".max_connections"), self.query_agent_max_conn))
        return template_zabbix.key_and_query(result)
