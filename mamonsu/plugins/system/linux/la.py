from mamonsu.plugins.system.plugin import SystemPlugin as Plugin


class La(Plugin):
    AgentPluginType = 'sys'
    query_agent = "cat /proc/loadavg | awk '{ print $1 }'"
    key = 'system.la{}'

    def run(self, zbx):
        la_1 = open('/proc/loadavg', 'r').read().split(' ')[0]
        zbx.send('system.la[1]', float(la_1))

    def items(self, template):
        return template.item({
            'name': 'System load average over 1 minute',
            'key': self.right_type(self.key, '1'),
        })

    def graphs(self, template):
        items = [{'key': self.right_type(self.key, '1')}]
        graph = {'name': 'System load average', 'items': items}
        return template.graph(graph)

    def keys_and_queries(self, template_zabbix):
        result = []
        result.append('system.la.1,{0}'.format(self.query_agent))
        return template_zabbix.key_and_query(result)

    def sql(self):
        result = {}  # key is name of file, var is query
        result['system.la'] = self.query_agent
        return result

