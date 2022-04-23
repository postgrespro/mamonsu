import mamonsu.lib.platform as platform
from mamonsu.lib.plugin import Plugin

if platform.LINUX:
    import resource


class Health(Plugin):

    AgentPluginType = "sys"

    DEFAULT_CONFIG = {
        "max_memory_usage": str(40 * 1024 * 1024)
    }

    counter = 0

    def run(self, zbx):
        zbx.send("mamonsu.plugin.keepalive[]", 0)
        if platform.LINUX:
            usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
            zbx.send("mamonsu.memory.rss[max]", usage)
        self.counter += 1
        if self.counter > 9:
            self.log.info("=== Keep alive ===")
            self.counter = 0

    def items(self, template, dashboard=False):
        # see supervisor.py:
        if self.Type == "mamonsu":
            result = template.item({
                "name": "Mamonsu: Plugin Errors",
                "key": "mamonsu.plugin.errors[]",
                "value_type": Plugin.VALUE_TYPE.text  # text
            }) + template.item({
                "name": "Mamonsu: Plugin Keep Alive",
                "key": self.right_type("mamonsu.plugin.keepalive{0}")
            })
            if platform.LINUX:
                result += template.item({
                    "name": "Mamonsu: RSS Memory Max Usage",
                    "key": "mamonsu.memory.rss[max]",
                    "units": Plugin.UNITS.bytes
                })
        else:
            result = template.item({
                "name": "Mamonsu: Plugin Keep Alive",
                "key": self.right_type("mamonsu.plugin.keepalive{0}")
            })
        if not dashboard:
            return result
        else:
            return []

    def triggers(self, template, dashboard=False):
        if self.Type == "mamonsu":
            result = template.trigger({
                "name": "Mamonsu plugin errors on {HOSTNAME}. {ITEM.LASTVALUE}",
                "expression": "{#TEMPLATE:mamonsu.plugin.errors[].strlen()}&gt;1"
            }) + template.trigger({
                "name": "Mamonsu nodata from {HOSTNAME}",
                "expression": "{#TEMPLATE:" + self.right_type("mamonsu.plugin.keepalive{0}") + ".nodata(180)}=1"
            })
            if platform.LINUX:
                result += template.trigger({
                    "name": "Mamonsu agent memory usage alert on {HOSTNAME}: {ITEM.LASTVALUE} bytes",
                    "expression": "{#TEMPLATE:mamonsu.memory.rss[max].last()}&gt;" + self.plugin_config(
                        "max_memory_usage")
                })
        else:
            result = template.trigger({
                "name": "Mamonsu nodata from {HOSTNAME}",
                "expression": "{#TEMPLATE:" + self.right_type("mamonsu.plugin.keepalive{0}") + ".nodata(180)}=1"
            })
        return result

    def keys_and_queries(self, template_zabbix):
        result = ["{0},{1}".format("mamonsu.plugin.keepalive", "echo 0")]
        return template_zabbix.key_and_query(result)
