from mamonsu.plugins.system.plugin import SystemPlugin as Plugin


class SystemUptime(Plugin):
    AgentPluginType = 'sys'

    DEFAULT_CONFIG = {'uptime': str(60 * 5)}
    query_agent = "cat /proc/uptime | awk '{ print $1 }'"

    def run(self, zbx):
        uptime = open('/proc/uptime', 'r').read().split(' ')[0]
        zbx.send('system.uptime[]', int(float(uptime)))

    def items(self, template):
        return template.item({
            'name': 'System uptime',
            'key': 'system.uptime[]',
            'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
            'units': Plugin.UNITS.uptime
        })

    def graphs(self, template):
        items = [{'key': 'system.uptime[]'}]
        graph = {'name': 'System uptime', 'items': items}
        return template.graph(graph)

    def triggers(self, template):
        return template.trigger({
            'name': 'System was restarted on '
            '{HOSTNAME} (uptime={ITEM.LASTVALUE})',
            'expression': '{#TEMPLATE:system.uptime[].last'
            '()}&lt;' + self.plugin_config('uptime')
        })

    def keys_and_queries(self, template_zabbix):
        result = []
        #result.append('system.uptime[],{0}'.format(self.query_agent))
        return template_zabbix.key_and_query(result)
