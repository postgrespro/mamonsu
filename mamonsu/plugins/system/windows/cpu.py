from .helpers import PerfData

from mamonsu.plugins.system.plugin import SystemPlugin as Plugin
from mamonsu.lib.zbx_template import ZbxTemplate


class Cpu(Plugin):
    MaxPrivilegedTime = 60

    Items = [
        (r'\Processor(*)\% User Time', "[user_time]", "User Time", Plugin.UNITS.percent, "578159"),
        (r'\Processor(*)\% Idle Time', "[idle_time]", "Idle Time", Plugin.UNITS.percent, "8B817C"),
        (r'\Processor(*)\% Privileged Time', "[privileged_time]", "Privileged Time", Plugin.UNITS.percent, "00B0B8"),
    ]

    def run(self, zbx):
        perf_services = []
        for _, item in enumerate(self.Items):
            perf_services.append(item[0])
        data = PerfData.get(perf_services, delay=1000)
        for idx, item in enumerate(self.Items):
            zbx.send("system.cpu{0}".format(item[1]), float(data[idx]))

    def items(self, template, dashboard=False):
        result = ""
        for item in self.Items:
            result += template.item({
                "name": "System: CPU {0}".format(item[2].lower()),
                "key": "system.cpu{0}".format(item[1]),
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
                    "key": "system.cpu{0}".format(item[1]),
                    "color": item[4]
                })
        graph = {
            "name": "System: CPU Overview",
            "items": items,
            "type": 1
        }
        if not dashboard:
            return template.graph(graph)
        else:
            return [
                {
                    "dashboard": {
                        "name": "System: CPU Overview",
                        "page": ZbxTemplate.dashboard_page_system_windows["name"],
                        "size": ZbxTemplate.dashboard_widget_size_medium,
                        "position": 0
                    }
                }
            ]

    def triggers(self, template, dashboard=False):
        return template.trigger({
            "name": "CPU privileged time is too big on {HOSTNAME}",
            "expression": "{#TEMPLATE:system.cpu[privileged_time].last()}&gt;" + str(self.MaxPrivilegedTime)
        })
