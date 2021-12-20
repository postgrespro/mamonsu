# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from distutils.version import LooseVersion
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate


class Instance(Plugin):
    AgentPluginType = "pg"
    query_agent = """
    SELECT sum({0}) AS {0}
    FROM pg_catalog.pg_stat_database;
    """
    key = "pgsql."
    Items = [
        # key, zbx_key, description,
        #    ('graph name', color, side), units, delta

        ("xact_commit", "transactions[committed]", "transactions: committed",
         ("PostgreSQL instance: rate", "0000CC", 1),
         Plugin.UNITS.none, Plugin.DELTA.speed_per_second),
        ("blks_hit", "blocks[hit]", "blocks: hit",
         ("PostgreSQL instance: rate", "00CC00", 0),
         Plugin.UNITS.none, Plugin.DELTA.speed_per_second),
        ("blks_read", "blocks[read]", "blocks: read",
         ("PostgreSQL instance: rate", "CC0000", 0),
         Plugin.UNITS.none, Plugin.DELTA.speed_per_second),

        ("conflicts", "events[conflicts]", "event: conflicts",
         ("PostgreSQL instance: events", "0000CC", 0),
         Plugin.UNITS.none, Plugin.DELTA.simple_change),
        ("deadlocks", "events[deadlocks]", "event: deadlocks",
         ("PostgreSQL instance: events", "000000", 0),
         Plugin.UNITS.none, Plugin.DELTA.simple_change),
        ("xact_rollback", "events[xact_rollback]", "event: rollbacks",
         ("PostgreSQL instance: events", "CC0000", 0),
         Plugin.UNITS.none, Plugin.DELTA.simple_change),

        ("temp_bytes", "temp[bytes]", "temp: bytes written",
         ("PostgreSQL instance: temp files", "CC0000", 0),
         Plugin.UNITS.bytes, Plugin.DELTA.simple_change),
        ("temp_files", "temp[files]", "temp: files created",
         ("PostgreSQL instance: temp files", "0000CC", 1),
         Plugin.UNITS.none, Plugin.DELTA.simple_change),

        # stacked
        ("tup_deleted", "tuples[deleted]", "tuples: deleted",
         ("PostgreSQL instance: tuples", "000000", 0),
         Plugin.UNITS.none, Plugin.DELTA.speed_per_second),
        ("tup_fetched", "tuples[fetched]", "tuples: fetched",
         ("PostgreSQL instance: tuples", "0000CC", 0),
         Plugin.UNITS.none, Plugin.DELTA.speed_per_second),
        ("tup_inserted", "tuples[inserted]", "tuples: inserted",
         ("PostgreSQL instance: tuples", "00CC00", 0),
         Plugin.UNITS.none, Plugin.DELTA.speed_per_second),
        ("tup_returned", "tuples[returned]", "tuples: returned",
         ("PostgreSQL instance: tuples", "CC00CC", 1),
         Plugin.UNITS.none, Plugin.DELTA.speed_per_second),
        ("tup_updated", "tuples[updated]", "tuples: updated",
         ("PostgreSQL instance: tuples", "CC0000", 0),
         Plugin.UNITS.none, Plugin.DELTA.speed_per_second),
    ]
    Items_pg_12 = [
        # key, zbx_key, description,
        #    ('graph name', color, side), units, delta
        ("checksum_failures", "events[checksum_failures]", "event: checksum_failures",
         ("PostgreSQL instance: events", "00FF00", 0),
         Plugin.UNITS.none, Plugin.DELTA.simple_change)
    ]

    def run(self, zbx):
        all_items = self.Items
        if Pooler.server_version_greater("12.0"):
            all_items = self.Items + self.Items_pg_12

        columns = ["sum(COALESCE({0}, 0)) as {0}".format(x[0]) for x in all_items]
        result = Pooler.query("""
        SELECT {0}
        FROM pg_catalog.pg_stat_database;
        """.format(", ".join(columns)))
        for key, value in enumerate(result[0]):
            zbx_key, value = "pgsql.{0}".format(all_items[key][1]), int(value)
            zbx.send(zbx_key, value, all_items[key][5], only_positive_speed=True)
        del columns, result

    def items(self, template, dashboard=False):
        result = ""
        for num, item in enumerate(self.Items + self.Items_pg_12):
            if self.Type == "mamonsu":
                delta = Plugin.DELTA.as_is
            else:
                delta = item[5]
            # split each item to get values for keys of both agent type and mamonsu type
            keys = item[1].split("[")
            result += template.item({
                "key": self.right_type(self.key + keys[0] + "{0}", keys[1][:-1]),
                "name": "PostgreSQL {0}".format(item[2]),
                "value_type": self.VALUE_TYPE.numeric_float,
                "units": item[4],
                "delay": self.plugin_config("interval"),
                "delta": delta
            })
        if not dashboard:
            return result
        else:
            return [{
                "dashboard": {"name": self.right_type(self.key + self.Items[6][1].split("[")[0] + "{0}",
                                                      self.Items[6][1].split("[")[1][:-1]),
                              "page": ZbxTemplate.dashboard_page_instance["name"],
                              "size": ZbxTemplate.dashboard_widget_size_medium,
                              "position": 5}
            },
                {
                    "dashboard": {"name": self.right_type(self.key + self.Items[7][1].split("[")[0] + "{0}",
                                                          self.Items[7][1].split("[")[1][:-1]),
                                  "page": ZbxTemplate.dashboard_page_instance["name"],
                                  "size": ZbxTemplate.dashboard_widget_size_medium,
                                  "position": 6}
                },
                {
                    "dashboard": {"name": self.right_type(self.key + self.Items[4][1].split("[")[0] + "{0}",
                                                          self.Items[4][1].split("[")[1][:-1]),
                                  "page": ZbxTemplate.dashboard_page_locks["name"],
                                  "size": ZbxTemplate.dashboard_widget_size_small,
                                  "position": 1}
                }]

    def graphs(self, template, dashboard=False):
        graphs_name = [
            "PostgreSQL instance: rate",
            "PostgreSQL instance: events",
            "PostgreSQL instance: temp files",
            "PostgreSQL instance: tuples"]
        result = ""
        for name in graphs_name:
            items = []
            for num, item in enumerate(self.Items + self.Items_pg_12):
                if item[3][0] == name:
                    # split each item to get values for keys of both agent type and mamonsu type
                    keys = item[1].split("[")
                    items.append({
                        "key": self.right_type(self.key + keys[0] + "{0}", keys[1][:-1]),
                        "color": item[3][1],
                        "yaxisside": item[3][2]
                    })
            graph = {
                "name": name,
                "items": items
            }
            result += template.graph(graph)

        if not dashboard:
            return result
        else:
            return [{
                "dashboard": {"name": "PostgreSQL instance: tuples",
                              "page": ZbxTemplate.dashboard_page_overview["name"],
                              "size": ZbxTemplate.dashboard_widget_size_medium,
                              "position": 6}
            },
                {
                    "dashboard": {"name": "PostgreSQL instance: events",
                                  "page": ZbxTemplate.dashboard_page_instance["name"],
                                  "size": ZbxTemplate.dashboard_widget_size_medium,
                                  "position": 4}
                }]

    def keys_and_queries(self, template_zabbix):
        result = []
        if LooseVersion(self.VersionPG) < LooseVersion("12"):
            all_items = self.Items
        else:
            all_items = self.Items + self.Items_pg_12
        for item in all_items:
            # split each item to get values for keys of both agent type and mamonsu type
            keys = item[1].split("[")
            result.append("{0}[*],$2 $1 -c \"{1}\"".format("{0}{1}.{2}".format(self.key, keys[0], keys[1][:-1]),
                                                           self.query_agent.format(format(item[0]))))
        return template_zabbix.key_and_query(result)
