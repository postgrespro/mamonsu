from .helpers import DiskInfo, PerfData

from mamonsu.plugins.system.plugin import SystemPlugin as Plugin


class DiskStats(Plugin):

    def run(self, zbx):
        devices = []
        for disk in DiskInfo.get_fixed_drivers():
            perf_services = [
                r'\LogicalDisk({0}:)\Disk Reads/sec'.format(disk),
                r'\LogicalDisk({0}:)\Disk Writes/sec'.format(disk),
                r'\LogicalDisk({0}:)\% Idle Time'.format(disk),
                r'\LogicalDisk({0}:)\Avg. Disk Queue Length'.format(disk)]
            data = PerfData.get(perf_services, delay=1000)
            zbx.send("system.disk.read[{0}]".format(disk), float(data[0]))
            zbx.send("system.disk.write[{0}]".format(disk), float(data[1]))
            zbx.send("system.disk.idle[{0}]".format(disk), float(data[2]))
            zbx.send("system.disk.queue_avg[{0}]".format(disk), float(data[3]))
            devices.append({"{#LOGICALDEVICE}": disk})
            del perf_services, data
        zbx.send("system.disk.discovery[]", zbx.json({"data": devices}))
        del devices

    def discovery_rules(self, template, dashboard=False):
        if Plugin.Type == "mamonsu":
            key_discovery = "system.disk.discovery[]"
        else:
            key_discovery = "system.disk.discovery"
        rule = {
            "name": "System: Logical Disks Discovery",
            "key": key_discovery
        }
        if Plugin.old_zabbix:
            rule["filter"] = "{#LOGICALDEVICE}:.*"
            conditions = []
        else:
            conditions = [
                {
                    "condition": [
                        {
                            "macro": "{#LOGICALDEVICE}",
                            "value": ".*",
                            "operator": 8,
                            "formulaid": "A"
                        }
                    ]
                }
            ]

        items = [
            {
                "key": "system.disk.read[{#LOGICALDEVICE}]",
                "name": "System: Logical Device {#LOGICALDEVICE} Read op/sec",
                "delta": Plugin.DELTA.speed_per_second
            },
            {
                "key": "system.disk.write[{#LOGICALDEVICE}]",
                "name": "System: Logical Device {#LOGICALDEVICE} Write op/sec",
                "delta": Plugin.DELTA.speed_per_second
            },
            {
                "key": "system.disk.queue_avg[{#LOGICALDEVICE}]",
                "name": "System: Logical Device {#LOGICALDEVICE} Queue"
            },
            {
                "key": "system.disk.idle[{#LOGICALDEVICE}]",
                "name": "System: Logical Device {#LOGICALDEVICE} Idle Time (%)",
                "units": Plugin.UNITS.percent
            }
        ]

        graphs = [
            {
                "name": "System: Logical Devices Overview {#LOGICALDEVICE}",
                "items": [
                    {
                        "color": "87C2B9",
                        "key": "system.disk.read[{#LOGICALDEVICE}]",
                        "drawtype": 2
                    },
                    {
                        "color": "793F5D",
                        "key": "system.disk.write[{#LOGICALDEVICE}]",
                        "drawtype": 2
                    },
                    {
                        "key": "system.disk.queue_avg[{#LOGICALDEVICE}]",
                        "name": "System: Logical Device {#LOGICALDEVICE} Queue",
                        "yaxisside": 1,
                        "drawtype": 2
                    }
                ]
            }
        ]

        return template.discovery_rule(rule=rule, conditions=conditions, items=items, graphs=graphs)
