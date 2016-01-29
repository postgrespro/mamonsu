from mamonsu.lib.plugin import Plugin


class Processes(Plugin):

    # alert fork-rate
    ForkRate = 500

    Items = [
        # key, zbx_key, name, delta, color, side
        ('procs_running', 'processes[running]',
            'in state running', 0, 'CC0000', 0),
        ('procs_blocked', 'processes[blocked]',
            'in state blocked', 0, '00CC00', 0),
        ('processes', 'processes[forkrate]',
            'forkrate', 1, '0000CC', 1),
    ]

    def run(self, zbx):
        with open('/proc/stat', 'r') as f:
            for line in f:
                data = line.split()
                for item in self.Items:
                    if data[0] == item[0]:
                        zbx.send('system.{0}'.format(item[1]), data[1])
                        break

    def items(self, template):
        result = ''
        for item in self.Items:
            result += template.item({
                'name': 'Processes: {0}'.format(item[2]),
                'key': 'system.{0}'.format(item[1]),
                'delta': item[3]
            })
        return result

    def graphs(self, template):
        items = []
        for item in self.Items:
            items.append({
                'key': 'system.{0}'.format(item[1]),
                'color': item[4],
                'yaxisside': item[5]
            })
        graph = {'name': 'Processes overview', 'items': items}
        return template.graph(graph)

    def triggers(self, template):
        return template.trigger({
            'name': 'Process fork-rate to '
            'frequently on {HOSTNAME}',
            'expression': '{#TEMPLATE:system.processes[forkrate]'
            '.last()}&gt;' + str(self.ForkRate)
        })
