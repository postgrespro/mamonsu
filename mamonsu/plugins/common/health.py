from mamonsu.lib.plugin import Plugin


class Health(Plugin):

    counter = 0

    def run(self, zbx):
        zbx.send('mamonsu.plugin.keepalive[]', 0)
        self.counter += 1
        if self.counter > 9:
            self.log.info('=== Keep alive ===')
            self.counter = 0

    def items(self, template):
        # see supervisor.py:
        return template.item({
            'name': 'Mamonsu: plugin errors',
            'key': 'mamonsu.plugin.errors[]',
            'value_type': Plugin.VALUE_TYPE.text  # text
        }) + template.item({
            'name': 'Mamonsu: plugin keep alive',
            'key': 'mamonsu.plugin.keepalive[]'
        })

    def triggers(self, template):
        return template.trigger({
            'name': 'Mamonsu plugin errors '
            'on {HOSTNAME}. {ITEM.LASTVALUE}',
            'expression': '{#TEMPLATE:mamonsu.plugin.errors[].strlen()'
            '}&gt;1'
        }) + template.trigger({
            'name': 'Mamonsu nodata from {HOSTNAME}',
            'expression': '{#TEMPLATE:mamonsu.plugin.keepalive[]'
            '.nodata(180)}=1'
        })
