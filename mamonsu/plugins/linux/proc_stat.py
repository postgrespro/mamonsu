import re
from mamonsu.lib.plugin import Plugin


class ProcStat(Plugin):

    # alert fork-rate
    ForkRate = 500
    # /proc/stat all cpu line
    re_stat = re.compile('cpu\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)')

    ProcessItems = [
        # key, zbx_key, name, delta, color, side
        ('procs_running', 'processes[running]',
            'in state running', 0, 'CC0000', 0),
        ('procs_blocked', 'processes[blocked]',
            'in state blocked', 0, '00CC00', 0),
        ('processes', 'processes[forkrate]',
            'forkrate', 1, '0000CC', 1),
    ]

    CpuItems = [
        # key, zbx_key, name, delta, color, side
        (1, 'cpu[user]',
            'by normal programs and daemons', 2, 'CC0000', 0),
        (2, 'cpu[nice]',
            'by nice(1)d programs', 2, '00CC00', 0),
        (3, 'cpu[system]',
            'by the kernel in system activities', 2, '0000CC', 0),
        (4, 'cpu[idle]',
            'Idle CPU time', 2, '00CC00', 0),
        (5, 'cpu[iowait]',
            'waiting for I/O operations', 2, '00CC00', 0),
        (6, 'cpu[irq]',
            'handling interrupts', 2, '00CC00', 0),
        (7, 'cpu[softirq]',
            'handling batched interrupts', 2, '00CC00', 0),
    ]

    def run(self, zbx):
        with open('/proc/stat', 'r') as f:
            for line in f:
                data = line.split()
                # parse processes
                for item in self.ProcessItems:
                    if data[0] == item[0]:
                        zbx.send('system.{0}'.format(item[1]), data[1])
                        break
                # parse cpu
                if data[0] == 'cpu':
                    m = self.re_stat.match(line)
                    if m is None:
                        continue
                    for item in self.CpuItems:
                        value = m.group(item[0])
                        zbx.send('system.{0}'.format(item[1]), int(value))

    def items(self, template):
        result = ''
        for item in self.ProcessItems:
            result += template.item({
                'name': 'Processes: {0}'.format(item[2]),
                'key': 'system.{0}'.format(item[1]),
                'delta': item[3]
            })
        for item in self.CpuItems:
            result += template.item({
                'name': 'CPU time spent {0}'.format(item[2]),
                'key': 'system.{0}'.format(item[1]),
                'delta': item[3]
            })
        return result

    def graphs(self, template):
        items = []
        for item in self.ProcessItems:
            items.append({
                'key': 'system.{0}'.format(item[1]),
                'color': item[4],
                'yaxisside': item[5]
            })
        graphs = template.graph({'name': 'Processes overview', 'items': items})
        for item in self.CpuItems:
            items.append({
                'key': 'system.{0}'.format(item[1]),
                'color': item[4],
                'yaxisside': item[5]
            })
        graphs += template.graph({'name': 'CPU time spent', 'items': items})
        return graphs

    def triggers(self, template):
        return template.trigger({
            'name': 'Process fork-rate to '
            'frequently on {HOSTNAME}',
            'expression': '{#TEMPLATE:system.processes[forkrate]'
            '.last()}&gt;' + str(self.ForkRate)
        })
