import re

from mamonsu.plugins.system.plugin import SystemPlugin as Plugin


class ProcStat(Plugin):
    AgentPluginType = 'sys'
    query_agent = "cat /proc/stat"
    query_agent_procs = ["cat /proc/stat | awk '/procs_running/ { print $2 }'",
                         "cat /proc/stat | awk '/procs_blocked/ { print $2 }'",
                         "cat /proc/stat | awk '/processes/ { print $2 }'"]
    query_agent_cpu = "expr `grep -w 'cpu' /proc/stat | awk '{print $"
    key = 'system.'
    # alert fork-rate
    ForkRate = 500
    # /proc/stat all cpu line
    re_stat = re.compile(
        'cpu\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)')

    ProcessItems = [
        # key, zbx_key, name, delta, color, side
        ('procs_running', 'processes[running]',
         'in state running', Plugin.DELTA.as_is, 'CC0000', 0),
        ('procs_blocked', 'processes[blocked]',
         'in state blocked', Plugin.DELTA.as_is, '00CC00', 0),
        ('processes', 'processes[forkrate]',
         'forkrate', Plugin.DELTA.speed_per_second, '0000CC', 1),
    ]

    CpuItems = [
        # key, zbx_key, name, delta, color, side
        (1, 'cpu[user]',
         'by normal programs and daemons',
         Plugin.DELTA.speed_per_second, '0000CC', 0),
        (2, 'cpu[nice]',
         'by nice(1)d programs',
         Plugin.DELTA.speed_per_second, 'CC00CC', 0),
        (3, 'cpu[system]',
         'by the kernel in system activities',
         Plugin.DELTA.speed_per_second, 'CC0000', 0),
        (4, 'cpu[idle]',
         'Idle CPU time',
         Plugin.DELTA.speed_per_second, '00CC00', 0),
        (5, 'cpu[iowait]',
         'waiting for I/O operations',
         Plugin.DELTA.speed_per_second, 'CCCC00', 0),
        (6, 'cpu[irq]',
         'handling interrupts',
         Plugin.DELTA.speed_per_second, '777777', 0),
        (7, 'cpu[softirq]',
         'handling batched interrupts',
         Plugin.DELTA.speed_per_second, '000077', 0),
    ]

    def run(self, zbx):
        with open('/proc/stat', 'r') as f:
            for line in f:
                data = line.split()
                # parse processes
                for item in self.ProcessItems:
                    if data[0] == item[0]:
                        value = int(data[1])
                        zbx.send(
                            'system.{0}'.format(item[1]), value, item[3])
                        break
                # parse cpu
                if data[0] == 'cpu':
                    m = self.re_stat.match(line)
                    if m is None:
                        continue
                    for item in self.CpuItems:
                        value = m.group(item[0])
                        zbx.send(
                            'system.{0}'.format(item[1]), int(value), item[3])

    def items(self, template):
        result = ''
        for item in self.ProcessItems:
            # split each item to get values for keys of both agent type and mamonsu type
            keys = item[1].split('[')
            result += template.item({
                'name': 'Processes: {0}'.format(item[2]),
                'key': self.right_type(self.key + keys[0] + '{0}', keys[1][:-1])
            })
        for item in self.CpuItems:
            # split each item to get values for keys of both agent type and mamonsu type
            keys = item[1].split('[')
            result += template.item({
                'name': 'CPU time spent {0}'.format(item[2]),
                'key': self.right_type(self.key + keys[0] + '{0}', keys[1][:-1])
            })
        return result

    def graphs(self, template):
        items = []
        for item in self.ProcessItems:
            # split each item to get values for keys of both agent type and mamonsu type
            keys = item[1].split('[')
            items.append({
                'key': self.right_type(self.key + keys[0] + '{0}', keys[1][:-1]),
                'color': item[4],
                'yaxisside': item[5]
            })
        graphs = template.graph({'name': 'Processes overview', 'items': items})
        items = []
        for item in self.CpuItems:
            # split each item to get values for keys of both agent type and mamonsu type
            keys = item[1].split('[')
            items.append({
                'key': self.right_type(self.key + keys[0] + '{0}', keys[1][:-1]),
                'color': item[4],
                'yaxisside': item[5]
            })
        graphs += template.graph({
            'name': 'CPU time spent',
            'items': items, 'type': self.GRAPH_TYPE.stacked})
        return graphs

    def triggers(self, template):
        return template.trigger({
            'name': 'Process fork-rate to '
                    'frequently on {HOSTNAME}',
            'expression': '{#TEMPLATE:' + self.right_type('system.processes{0}', 'forkrate') +
                          '.min(5m)}&gt;' + str(self.ForkRate)
        })

    def keys_and_queries(self, template_zabbix):
        result = []
        for i, item in enumerate(self.ProcessItems):
            # split each item to get values for keys of both agent type and mamonsu type
            keys = item[1].split('[')
            result.append(
                '{0},{1}'.format('{0}{1}.{2}'.format(self.key.format(""), keys[0], keys[1][:-1]),
                                               self.query_agent_procs[i]))
        for i, item in enumerate(self.CpuItems):
            # split each item to get values for keys of both agent type and mamonsu type
            keys = item[1].split('[')
            result.append(
                '{0},{1}'.format('{0}{1}.{2}'.format(self.key.format(""), keys[0], keys[1][:-1]),
                                               self.query_agent_cpu + str(i + 2) + "}'`"))
        return template_zabbix.key_and_query(result)

    def sql(self):
        result = {}  # key is name of file, var is query
        result['system.proc_stat'] = self.query_agent
        return result
