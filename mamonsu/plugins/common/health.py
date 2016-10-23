import mamonsu.lib.platform as platform
from mamonsu.lib.plugin import Plugin

if platform.LINUX:
    import resource


class Health(Plugin):

    DEFAULT_CONFIG = {'max_memory_usage': str(40 * 1024 * 1024)}

    counter = 0

    def run(self, zbx):
        zbx.send('mamonsu.plugin.keepalive[]', 0)
        if platform.LINUX:
            usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
            zbx.send('mamonsu.memory.rss[max]', usage)
        self.counter += 1
        if self.counter > 9:
            self.log.info('=== Keep alive ===')
            self.counter = 0

    def items(self, template):
        # see supervisor.py:
        result = template.item({
            'name': 'Mamonsu: plugin errors',
            'key': 'mamonsu.plugin.errors[]',
            'value_type': Plugin.VALUE_TYPE.text  # text
        }) + template.item({
            'name': 'Mamonsu: plugin keep alive',
            'key': 'mamonsu.plugin.keepalive[]'
        })
        if platform.LINUX:
            result += template.item({
                'name': 'Mamonsu: rss memory max usage',
                'key': 'mamonsu.memory.rss[max]',
                'units': Plugin.UNITS.bytes
            })
        return result

    def triggers(self, template):
        result = template.trigger({
            'name': 'Mamonsu plugin errors '
            'on {HOSTNAME}. {ITEM.LASTVALUE}',
            'expression': '{#TEMPLATE:mamonsu.plugin.errors[].strlen()'
            '}&gt;1'
        }) + template.trigger({
            'name': 'Mamonsu nodata from {HOSTNAME}',
            'expression': '{#TEMPLATE:mamonsu.plugin.keepalive[]'
            '.nodata(180)}=1'
        })
        if platform.LINUX:
            result += template.trigger({
                'name': 'Mamonsu agent memory usage alert '
                'on {HOSTNAME}: {ITEM.LASTVALUE} bytes',
                'expression': '{#TEMPLATE:mamonsu.memory.rss[max].last()}'
                '&gt;' + self.plugin_config('max_memory_usage')
            })
        return result
