# -*- coding: utf-8 -*-

from mamonsu.plugins.pgsql.plugin import PgsqlPlugin as Plugin
from .pool import Pooler
from mamonsu.lib.zbx_template import ZbxTemplate


class BgWriter(Plugin):
    AgentPluginType = "pg"
    key = "pgsql.bgwriter{0}"
    query = """
    SELECT {0}
    FROM pg_catalog.pg_stat_bgwriter;
    """
    Items = [
        # key, zbx_key, description,
        #    ('graph name', color, side), units, delta

        ("buffers_checkpoint", "bgwriter[buffers_checkpoint]",
         "Buffers Written During Checkpoints",
         ("PostgreSQL bgwriter", "006AAE", 1),
         Plugin.DELTA.simple_change),

        ("buffers_clean", "bgwriter[buffers_clean]",
         "Buffers Written",
         ("PostgreSQL bgwriter", "00CC00", 1),
         Plugin.DELTA.simple_change),

        ("maxwritten_clean", "bgwriter[maxwritten_clean]",
         "Number of bgwriter Stopped by Max Write Count",
         ("PostgreSQL bgwriter", "FF5656", 0),
         Plugin.DELTA.simple_change),

        ("buffers_backend", "bgwriter[buffers_backend]",
         "Buffers Written Directly by a Backend",
         ("PostgreSQL bgwriter", "9C8A4E", 1),
         Plugin.DELTA.simple_change),

        ("buffers_backend_fsync", "bgwriter[buffers_backend_fsync]",
         "Times a Backend Execute Its Own Fsync",
         ("PostgreSQL bgwriter", "00CC00", 0),
         Plugin.DELTA.simple_change),

        ("buffers_alloc", "bgwriter[buffers_alloc]",
         "Buffers Allocated",
         ("PostgreSQL bgwriter", "FF5656", 1),
         Plugin.DELTA.simple_change)
    ]

    graph_name_buffers = "PostgreSQL bgwriter: Buffers"
    graph_name_ws = "PostgreSQL bgwriter: Write/Sync"

    def run(self, zbx):
        columns = [x[0] for x in self.Items]
        result = Pooler.query(self.query.format(", ".join(columns)))
        for key, value in enumerate(result[0]):
            zbx_key, value = "pgsql.{0}".format(self.Items[key][1]), int(value)
            zbx.send(zbx_key, value, self.Items[key][4])
        del columns, result

    def items(self, template, dashboard=False):
        result = ""
        if self.Type == "mamonsu":
            delta = Plugin.DELTA.as_is
        else:
            delta = Plugin.DELTA.simple_change
        for item in self.Items:
            result += template.item({
                "key": self.right_type(self.key, item[0]),
                "name": "PostgreSQL bgwriter: {0}".format(item[2]),
                "value_type": self.VALUE_TYPE.numeric_unsigned,
                "delay": self.plugin_config("interval"),
                "delta": delta
            })
        if not dashboard:
            return result
        else:
            return []

    def graphs(self, template, dashboard=False):
        items_buffers, items_write_sync = [], []
        for item in self.Items:
            if item[3][2] == 0:
                items_write_sync.append({
                    "key": self.right_type(self.key, item[0]),
                    "color": item[3][1],
                    "drawtype": 2
                })
            if item[3][2] == 1:
                items_buffers.append({
                    "key": self.right_type(self.key, item[0]),
                    "color": item[3][1],
                    "drawtype": 2
                })
        result = template.graph({
            "name": self.graph_name_buffers,
            "items": items_buffers
        }) + template.graph({
            "name": self.graph_name_ws,
            "items": items_write_sync
        })
        if not dashboard:
            return result
        else:
            return [{
                "dashboard": {"name": self.graph_name_buffers,
                              "page": ZbxTemplate.dashboard_page_overview["name"],
                              "size": ZbxTemplate.dashboard_widget_size_medium,
                              "position": 7}
            },
                {
                    "dashboard": {"name": self.graph_name_ws,
                                  "page": ZbxTemplate.dashboard_page_overview["name"],
                                  "size": ZbxTemplate.dashboard_widget_size_medium,
                                  "position": 8}
                }]

    def keys_and_queries(self, template_zabbix):
        result = []
        for item in self.Items:
            # delete from key '[' and ']' in Item for zabbix agent
            result.append("{0}[*],$2 $1 -c \"{1}\"".format(self.key.format("." + item[0]), self.query.format(item[0])))
        return template_zabbix.key_and_query(result)
