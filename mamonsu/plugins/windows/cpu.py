from mamonsu.lib.plugin import Plugin
from .helpers import PerfData


class Cpu(Plugin):

    MaxPrivilegedTime = 60

    Items = [

        (r'\Processor(*)\% User Time', '[user_time]',
            'User time', '%', ('CC0000')),

        (r'\Processor(*)\% Idle Time', '[idle_time]',
            'Idle time', '%', ('00CC00')),

        (r'\Processor(*)\% Privileged Time', '[privileged_time]',
            'Privileged time', '%', ('770000')),

    ]

    def run(self, zbx):
        perf_services = []
        for item in self.Items:
            perf_services.insert(0, item[0])
        data = PerfData.get(perf_services, delay=1000)
        for idx, item in enumerate(self.Items):
            zbx.send('system.cpu{0}'.format(item[1]), data[idx])

    def items(self, template):
        result = ''
        for item in self.Items:
            result += template.item({
                'name': '{0}'.format(item[2]),
                'key': 'system.cpu{0}'.format(item[1]),
                'units': item[3]
            })
        return result

    def graphs(self, template):
        items = []
        for item in self.Items:
            if item[4] is not None:
                items.append({
                    'key': 'system.cpu{0}'.format(item[1]),
                    'color': item[4]
                })
        graph = {'name': 'CPU overview', 'items': items, 'type': 1}
        return template.graph(graph)

    def triggers(self, template):
        return template.trigger({
            'name': 'CPU privileged time'
            'is too big on {HOSTNAME}',
            'expression': '{#TEMPLATE:system.cpu[privileged_time]'
            '.last()}&gt;' + str(self.MaxPrivilegedTime)
        })
