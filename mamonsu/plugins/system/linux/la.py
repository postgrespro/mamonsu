from mamonsu.plugins.system.plugin import SystemPlugin as Plugin


class La(Plugin):

    def run(self, zbx):
        la_1 = open('/proc/loadavg', 'r').read().split(' ')[0]
        zbx.send('system.la[1]', float(la_1))

    def items(self, template):
        return template.item({
            'name': 'System load average over 1 minute',
            'key': 'system.la[1]'
        })

    def graphs(self, template):
        items = [{'key': 'system.la[1]'}]
        graph = {'name': 'System load average', 'items': items}
        return template.graph(graph)
