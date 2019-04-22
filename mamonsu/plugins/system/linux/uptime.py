from mamonsu.plugins.system.plugin import SystemPlugin as Plugin


class SystemUptime(Plugin):
    AgentPluginType = 'sys'

    DEFAULT_CONFIG = {'up_time': str(60 * 5)}
    query_agent = "cat /proc/uptime | awk '{ print $1 }'"

    def run(self, zbx):
        uptime = open('/proc/uptime', 'r').read().split(' ')[0]
        zbx.send('system.up_time[]', int(float(uptime)))

    def items(self, template):
        if Plugin.Type == "mamonsu":
            return template.item({
                'name': 'System up_time',
                'key': 'system.up_time[]',
                'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
                'units': Plugin.UNITS.uptime
            })
        else:
            return template.item({
                'name': 'System up_time',
                'key': 'system.up_time[]',
                'value_type': Plugin.VALUE_TYPE.numeric_float,
                'units': Plugin.UNITS.uptime
            })

    def graphs(self, template):
        items = [{'key': 'system.up_time[]'}]
        graph = {'name': 'System up_time', 'items': items}
        return template.graph(graph)

    def triggers(self, template):
        return template.trigger({
            'name': 'System was restarted on '
            '{HOSTNAME} (up_time={ITEM.LASTVALUE})',
            'expression': '{#TEMPLATE:system.up_time[].last'
            '()}&lt;' + self.plugin_config('up_time')
        })

    def keys_and_queries(self, template_zabbix):
        result = []
        result.append('system.up_time[],{0}'.format(self.query_agent))
        return template_zabbix.key_and_query(result)
