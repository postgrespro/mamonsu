# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate


class Checkpoint(Plugin):
    AgentPluginType = "pg"
    Interval = 60 * 5

    query = """
    SELECT {0}
    FROM pg_catalog.pg_stat_bgwriter;
    """  # for mamonsu and agent
    query_interval = """
    SELECT {0}*3600
    FROM pg_catalog.pg_stat_bgwriter;
    """  # for mamonsu and agent checkpoints in hour
    key = "pgsql.checkpoint{0}"

    # key: (macro, value)
    plugin_macros = {
        "max_checkpoint_by_wal_in_hour": [("macro", "{$MAX_CHECKPOINT_BY_WAL_IN_HOUR}"), ("value", 12)]
    }

    Items = [
        # key, zbx_key, description,
        #    ('graph name', color, side), units, delta, factor

        ("checkpoints_timed", "count_timed",
         "by Timeout (in hour)",
         ("PostgreSQL Checkpoints: Count (in hour)", "00CC00", 0),
         Plugin.UNITS.none, Plugin.DELTA.speed_per_second, 60 * 60),

        ("checkpoints_req", "count_wal",
         "by WAL (in hour)",
         ("PostgreSQL Checkpoints: Count (in hour)", "FF5656", 0),
         Plugin.UNITS.none, Plugin.DELTA.speed_per_second, 60 * 60),

        ("checkpoint_write_time", "write_time",
         "Write Time",
         ("PostgreSQL Checkpoints: Write/Sync", "00CC00", 1),
         Plugin.UNITS.ms, Plugin.DELTA.speed_per_second, 1),

        ("checkpoint_sync_time", "checkpoint_sync_time",
         "Sync Time",
         ("PostgreSQL Checkpoints: Write/Sync", "FF5656", 1),
         Plugin.UNITS.ms, Plugin.DELTA.speed_per_second, 1)
    ]

    graph_name_count = "PostgreSQL Checkpoints: Count (in hour)"
    graph_name_ws = "PostgreSQL Checkpoints: Write/Sync"

    def run(self, zbx):
        columns = [x[0] for x in self.Items]
        result = Pooler.query(self.query.format(", ".join(columns)))
        for key, value in enumerate(result[0]):
            zbx_key, value = "pgsql.checkpoint[{0}]".format(self.Items[key][1]), int(value)
            zbx.send(zbx_key, value * self.Items[key][6], self.Items[key][5])
        del columns, result

    def items(self, template, dashboard=False):
        result = ""
        if self.Type == "mamonsu":
            delta = Plugin.DELTA.as_is
        else:
            delta = Plugin.DELTA.speed_per_second
        for item in self.Items:
            result += template.item({
                "key": self.right_type(self.key, item[1]),
                "name": "PostgreSQL Checkpoints: {0}".format(item[2]),
                "value_type": Plugin.VALUE_TYPE.numeric_float,
                "units": item[4],
                "delay": self.plugin_config("interval"),
                "delta": delta
            })
        if not dashboard:
            return result
        else:
            return []

    def graphs(self, template, dashboard=False):
        items_checkpoints, items_checkpoints_write_sync = [], []
        for item in self.Items:
            if item[3][2] == 0:
                items_checkpoints.append({
                    "key": self.right_type(self.key, item[1]),
                    "color": item[3][1],
                    "delay": self.Interval,
                    "drawtype": 2
                })
            if item[3][2] == 1:
                items_checkpoints_write_sync.append({
                    "key": self.right_type(self.key, item[1]),
                    "color": item[3][1],
                    "delay": self.Interval,
                    "drawtype": 2
                })
        result = template.graph({
            "name": self.graph_name_count,
            "items": items_checkpoints
        }) + template.graph({
             "name": self.graph_name_ws,
             "items": items_checkpoints_write_sync
        })
        if not dashboard:
            return result
        else:
            return [{
                "dashboard": {"name": "PostgreSQL Checkpoints: Count (in hour)",
                              "page": ZbxTemplate.dashboard_page_overview["name"],
                              "size": ZbxTemplate.dashboard_widget_size_medium,
                              "position": 9}
            },
                {
                    "dashboard": {"name": "PostgreSQL Checkpoints: Write/Sync",
                                  "page": ZbxTemplate.dashboard_page_overview["name"],
                                  "size": ZbxTemplate.dashboard_widget_size_medium,
                                  "position": 10}
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
            "name": "PostgreSQL Checkpoints: required checkpoints occurs too frequently on {HOSTNAME}",
            "expression": "{#TEMPLATE:" + self.right_type(self.key,
                                                          self.Items[1][1]) + ".last()}&gt;" + self.plugin_macros["max_checkpoint_by_wal_in_hour"][0][1]
        })

    def keys_and_queries(self, template_zabbix):
        result = []
        for num, item in enumerate(self.Items):
            if num > 1:
                result.append(
                    "{0}[*],$2 $1 -c \"{1}\"".format(self.key.format("." + item[1]), self.query.format(item[0])))
            else:
                result.append(
                    "{0}[*],$2 $1 -c \"{1}\"".format(self.key.format("." + item[1]),
                                                     self.query_interval.format(item[0])))
        return template_zabbix.key_and_query(result)
