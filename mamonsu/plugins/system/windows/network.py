from mamonsu.plugins.system.plugin import SystemPlugin as Plugin
from .helpers import PerfData
from mamonsu.lib.zbx_template import ZbxTemplate


class Network(Plugin):

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

    def items(self, template, dashboard=False):
        result = ''
        for item in self.Items:
            result += template.item({
                'name': 'Network {0}'.format(item[2].lower()),
                'key': 'system.network{0}'.format(item[1]),
                'units': item[3]
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
                    'key': 'system.network{0}'.format(item[1]),
                    'color': item[4][0],
                    'yaxisside': item[4][1]
                })
        graph = {
            'name': 'Network overview', 'items': items, 'type': 1}
        if not dashboard:
            return template.graph(graph)
        else:
            return [{'dashboard': {'name': 'Network overview',
                                   'page': ZbxTemplate.dashboard_page_system_windows['name'],
                                   'size': ZbxTemplate.dashboard_widget_size_medium,
                                   'position': 2}}]
