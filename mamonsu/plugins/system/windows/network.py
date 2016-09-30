import mamonsu.lib.platform as platform
from mamonsu.plugins.system.plugin import SystemPlugin as Plugin
from .helpers import PerfData


class Network(Plugin):

    if platform.PY2:
        _item = [
            r'\\Network Interface(*)\Output Queue Length',
            r'\\Network Interface(*)\Bytes Total/sec']
    elif platform.PY3:
        _item = [
            r'\Network Interface(*)\Output Queue Length',
            r'\Network Interface(*)\Bytes Total/sec']

    Items = [
        # perf_item, zbx_key, desc, delta, unit, (color, site)
        (_item[0], '[total_output_queue]',
            'Output Queue Length', None, ('0000CC', 0)),

        (_item[1], '[total_bytes]',
            'Bytes Total', 'b', ('00CC00', 1))
    ]

    def run(self, zbx):
        perf_services = []
        for _, item in enumerate(self.Items):
            perf_services.append(item[0])
        data = PerfData.get(perf_services, delay=1000)
        for idx, item in enumerate(self.Items):
            zbx.send('system.network{0}'.format(item[1]), float(data[idx]))

    def items(self, template):
        result = ''
        for item in self.Items:
            result += template.item({
                'name': 'Network {0}'.format(item[2].lower()),
                'key': 'system.network{0}'.format(item[1]),
                'units': item[3]
            })
        return result

    def graphs(self, template):
        items = []
        for item in self.Items:
            if item[4] is not None:
                items.append({
                    'key': 'system.network{0}'.format(item[1]),
                    'color': item[4][0],
                    'yaxisside': item[4][1]
                })
        graph = {
            'name': 'Network overview', 'items': items, 'type': 1}
        return template.graph(graph)
