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
         "bgwriter: buffers written during checkpoints",
         ("PostgreSQL bgwriter", "CCCC00", 1),
         Plugin.DELTA.simple_change),

        ("buffers_clean", "bgwriter[buffers_clean]",
         "bgwriter: buffers written",
         ("PostgreSQL bgwriter", "0000CC", 1),
         Plugin.DELTA.simple_change),

        ("maxwritten_clean", "bgwriter[maxwritten_clean]",
         "bgwriter: number of bgwriter stopped by max write count",
         ("PostgreSQL bgwriter", "777777", 0),
         Plugin.DELTA.simple_change),

        ("buffers_backend", "bgwriter[buffers_backend]",
         "bgwriter: buffers written directly by a backend",
         ("PostgreSQL bgwriter", "CC0000", 1),
         Plugin.DELTA.simple_change),

        ("buffers_backend_fsync", "bgwriter[buffers_backend_fsync]",
         "bgwriter: times a backend execute its own fsync",
         ("PostgreSQL bgwriter", "CC00CC", 0),
         Plugin.DELTA.simple_change),

        ("buffers_alloc", "bgwriter[buffers_alloc]",
         "bgwriter: buffers allocated",
         ("PostgreSQL bgwriter", "00CC00", 1),
         Plugin.DELTA.simple_change)
    ]

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
                "name": "PostgreSQL {0}".format(item[2]),
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
                    "color": item[3][1]
                })
            if item[3][2] == 1:
                items_buffers.append({
                    "key": self.right_type(self.key, item[0]),
                    "color": item[3][1]
                })
        result = template.graph({
            "name": "PostgreSQL bgwriter buffers",
            "items": items_buffers
        }) + \
                 template.graph({
                     "name": "PostgreSQL bgwriter write/sync",
                     "items": items_write_sync
                 })
        if not dashboard:
            return result
        else:
            return [{
                "dashboard": {"name": "PostgreSQL bgwriter buffers",
                              "page": ZbxTemplate.dashboard_page_overview["name"],
                              "size": ZbxTemplate.dashboard_widget_size_medium,
                              "position": 7}
            },
                {
                    "dashboard": {"name": "PostgreSQL bgwriter write/sync",
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
