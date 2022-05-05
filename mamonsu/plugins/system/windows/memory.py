from mamonsu.plugins.system.plugin import Plugin
from .helpers import PerfData
from mamonsu.lib.zbx_template import ZbxTemplate


class Memory(Plugin):
    Items = [
        # perf_item, zbx_key, desc, delta, unit, (color, site)
        (r"\Memory\Cache Bytes", "[cache]", "Memory Cached", Plugin.UNITS.bytes, ("9C8A4E", 0)),
        (r"\Memory\Available Bytes", "[available]", "Memory Available", Plugin.UNITS.bytes, ("00CC00", 0)),
        (r"\Memory\Free & Zero Page List Bytes", "[free]", "Memory Free", Plugin.UNITS.bytes, ("3B415A", 0))
    ]

    def run(self, zbx):
        perf_services = []
        for _, item in enumerate(self.Items):
            perf_services.append(item[0])
        data = PerfData.get(perf_services, delay=1000)
        for idx, item in enumerate(self.Items):
            zbx.send("system.memory{0}".format(item[1]), int(data[idx]))

    def items(self, template, dashboard=False):
        result = ""
        for item in self.Items:
            result += template.item({
                "name": "System: {0}".format(item[2]),
                "key": "system.memory{0}".format(item[1]),
                "units": item[3]
            })
        if not dashboard:
            return result
        else:
            return []

    def graphs(self, template, dashboard=False):
        items = []
        for item in self.Items:
            if item[4] is not None:
                items.append({
                    "key": "system.memory{0}".format(item[1]),
                    "color": item[4][0],
                    "yaxisside": item[4][1],
                    "drawtype": 1
                })
        graph = {
            "name": "System: Memory Overview",
            "items": items,
            "type": 1
        }
        if not dashboard:
            return template.graph(graph)
        else:
            return [{
                "dashboard": {
                    "name": "System: Memory Overview",
                    "page": ZbxTemplate.dashboard_page_system_windows["name"],
                    "size": ZbxTemplate.dashboard_widget_size_medium,
                    "position": 1
                }
            }]
