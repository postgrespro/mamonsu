from mamonsu.plugins.system.plugin import SystemPlugin as Plugin


class OpenFiles(Plugin):
    query_agent = "cat  /proc/sys/fs/file-nr | awk '{ print $1 }'"
    AgentPluginType = 'sys'
    key = "system.open_files[]"

    def run(self, zbx):
        open_files = open('/proc/sys/fs/file-nr', 'r').read().split("\t")[0]
        zbx.send('system.open_files[]', int(open_files))

    def items(self, template):
        return template.item({
            'name': 'Opened files',
            'key': 'system.open_files[]',
            'value_type': Plugin.VALUE_TYPE.numeric_unsigned
        })

    def graphs(self, template):
        items = [{'key': 'system.open_files[]'}]
        graph = {'name': 'System: count of opened files', 'items': items}
        return template.graph(graph)

    def keys_and_queries(self, template_zabbix):
        result = []
        result.append('{0},{1}'.format(self.key, self.query_agent))
        return template_zabbix.key_and_query(result)
