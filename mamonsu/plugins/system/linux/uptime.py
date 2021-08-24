from mamonsu.plugins.system.plugin import SystemPlugin as Plugin


class SystemUptime(Plugin):
    AgentPluginType = 'sys'

    DEFAULT_CONFIG = {'up_time': str(60 * 5)}
    query_agent = "cat /proc/uptime | awk '{ print int($1) }'"
    key = 'system.up_time{0}'

    def run(self, zbx):
        uptime = open('/proc/uptime', 'r').read().split(' ')[0]
        zbx.send('system.up_time[]', int(float(uptime)))

    def items(self, template, dashboard=False):
        if not dashboard:
            return template.item({
                'name': 'System up_time',
                'key': self.right_type(self.key),
                'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
                'delay': self.plugin_config('interval'),
                'units': Plugin.UNITS.uptime
            })
        else:
            return []

    def triggers(self, template, dashboard=False):
        return template.trigger({
            'name': 'System was restarted on '
                    '{HOSTNAME} (up_time={ITEM.LASTVALUE})',
            'expression': '{#TEMPLATE:' + self.right_type(self.key) + '.last'
                                                                      '()}&lt;' + self.plugin_config('up_time')
        })

    def keys_and_queries(self, template_zabbix):
        result = ['system.up_time,{0}'.format(self.query_agent)]
        return template_zabbix.key_and_query(result)
