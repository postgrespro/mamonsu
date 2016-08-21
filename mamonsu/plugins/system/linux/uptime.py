from mamonsu.plugins.system.plugin import SystemPlugin as Plugin


class Uptime(Plugin):

    def __init__(self, config):
        super(Uptime, self).__init__(config)
        self.TriggerUptimeLessThen = self.config.fetch(
            'system', 'uptime', int)

    def run(self, zbx):
        uptime = open('/proc/uptime', 'r').read().split(' ')[0]
        zbx.send('system.uptime[]', float(uptime))

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
            '()}&lt;' + str(self.TriggerUptimeLessThen)
        })
