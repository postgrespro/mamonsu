import re

from mamonsu.plugins.system.plugin import SystemPlugin as Plugin
from mamonsu.lib.zbx_template import ZbxTemplate


class ProcStat(Plugin):
    AgentPluginType = "system"

    query_agent = "cat /proc/stat"
    query_agent_procs = ["cat /proc/stat | awk '/procs_running/ { print $2 }'",
                         "cat /proc/stat | awk '/procs_blocked/ { print $2 }'",
                         "cat /proc/stat | awk '/processes/ { print $2 }'"]
    query_agent_cpu = "expr `grep -w 'cpu' /proc/stat | awk '{print $"
    key = "system."
    # alert fork-rate
    ForkRate = 500
    # /proc/stat all cpu line
    re_stat = re.compile("cpu\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")

    ProcessItems = [
        # key, zbx_key, name, delta, color, side
        ("procs_running", "processes[running]", "in State Running", Plugin.DELTA.as_is, "578159", 0),
        ("procs_blocked", "processes[blocked]", "in State Blocked", Plugin.DELTA.as_is, "E57862", 0),
        ("processes", "processes[forkrate]", "Forkrate", Plugin.DELTA.speed_per_second, "9C8A4E", 1),
    ]

    CpuItems = [
        # key, zbx_key, name, delta, color, side
        (1, "cpu[user]", "by Normal Programs and Daemons", Plugin.DELTA.speed_per_second, "578159", 0),
        (2, "cpu[nice]", "by nice(1)d Programs", Plugin.DELTA.speed_per_second, "793F5D", 0),
        (3, "cpu[system]", "by the Kernel in System Activities", Plugin.DELTA.speed_per_second, "9C8A4E", 0),
        (4, "cpu[idle]", "Idle", Plugin.DELTA.speed_per_second, "8B817C", 0),
        (5, "cpu[iowait]", "Waiting for I/O Operations", Plugin.DELTA.speed_per_second, "0082A5", 0),
        (6, "cpu[irq]", "Handling Interrupts", Plugin.DELTA.speed_per_second, "3B415A", 0),
        (7, "cpu[softirq]", "Handling Batched Interrupts", Plugin.DELTA.speed_per_second, "F6CB93", 0),
    ]

    def run(self, zbx):
        with open("/proc/stat", "r") as f:
            for line in f:
                data = line.split()
                # parse processes
                for item in self.ProcessItems:
                    if data[0] == item[0]:
                        value = int(data[1])
                        zbx.send(
                            "system.{0}".format(item[1]), value, item[3])
                        break
                # parse cpu
                if data[0] == "cpu":
                    m = self.re_stat.match(line)
                    if m is None:
                        continue
                    for item in self.CpuItems:
                        value = m.group(item[0])
                        zbx.send(
                            "system.{0}".format(item[1]), int(value), item[3])

    def items(self, template, dashboard=False):
        result = ""
        delta = Plugin.DELTA.as_is
        for i, item in enumerate(self.ProcessItems):
            # split each item to get values for keys of both agent type and mamonsu type
            keys = item[1].split("[")
            if i == 2 and Plugin.Type == "agent":
                delta = Plugin.DELTA.speed_per_second
            result += template.item({
                "name": "System: Processes {0}".format(item[2]),
                "key": self.right_type(self.key + keys[0] + "{0}", keys[1][:-1]),
                "delay": self.plugin_config("interval"),
                "delta": delta
            })
        if Plugin.Type == "mamonsu":
            delta = Plugin.DELTA.as_is
        else:
            delta = Plugin.DELTA.speed_per_second
        for item in self.CpuItems:
            # split each item to get values for keys of both agent type and mamonsu type
            keys = item[1].split("[")
            result += template.item({
                "name": "System: CPU Time Spent {0}".format(item[2]),
                "key": self.right_type(self.key + keys[0] + "{0}", keys[1][:-1]),
                "delay": self.plugin_config("interval"),
                "delta": delta
            })
        if not dashboard:
            return result
        else:
            return []

    def graphs(self, template, dashboard=False):
        items = []
        for item in self.ProcessItems:
            # split each item to get values for keys of both agent type and mamonsu type
            keys = item[1].split("[")
            items.append({
                "key": self.right_type(self.key + keys[0] + "{0}", keys[1][:-1]),
                "color": item[4],
                "yaxisside": item[5]
            })
        graphs = template.graph({
            "name": "System: Processes Overview",
            "items": items
        })
        items = []
        for item in self.CpuItems:
            # split each item to get values for keys of both agent type and mamonsu type
            keys = item[1].split("[")
            items.append({
                "key": self.right_type(self.key + keys[0] + "{0}", keys[1][:-1]),
                "color": item[4],
                "yaxisside": item[5]
            })
        graphs += template.graph({
            "name": "System: CPU Time Spent",
            "items": items, "type": self.GRAPH_TYPE.stacked
        })
        if not dashboard:
            return graphs
        else:
            return [
                {
                    "dashboard": {
                        "name": "System: CPU Time Spent",
                        "page": ZbxTemplate.dashboard_page_overview["name"],
                        "size": ZbxTemplate.dashboard_widget_size_medium,
                        "position": 3
                    }
                },
                {
                    "dashboard": {
                        "name": "System: Processes Overview",
                        "page": ZbxTemplate.dashboard_page_system_linux["name"],
                        "size": ZbxTemplate.dashboard_widget_size_medium,
                        "position": 3}
                }
            ]

    def triggers(self, template, dashboard=False):
        return template.trigger(
            {
                "name": "Process fork-rate to frequently on {HOSTNAME}",
                "expression": "{#TEMPLATE:" + self.right_type("system.processes{0}", "forkrate") +
                              ".min(5m)}&gt;" + str(self.ForkRate)
            }
        )

    def keys_and_queries(self, template_zabbix):
        result = []
        for i, item in enumerate(self.ProcessItems):
            # split each item to get values for keys of both agent type and mamonsu type
            keys = item[1].split("[")
            result.append(
                "{0},{1}".format("{0}{1}.{2}".format(self.key.format(""), keys[0], keys[1][:-1]),
                                 self.query_agent_procs[i]))
        for i, item in enumerate(self.CpuItems):
            # split each item to get values for keys of both agent type and mamonsu type
            keys = item[1].split("[")
            result.append("{0},{1}".format("{0}{1}.{2}".format(self.key.format(""), keys[0], keys[1][:-1]),
                                           self.query_agent_cpu + str(i + 2) + "}'`"))
        return template_zabbix.key_and_query(result)
