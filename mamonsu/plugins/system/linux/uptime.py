from mamonsu.plugins.system.plugin import SystemPlugin as Plugin


class SystemUptime(Plugin):
    AgentPluginType = "sys"

    # key: (macro, value)
    plugin_macros = {
        "system_uptime": [("macro", "{$SYSTEM_UPTIME}"), ("value", 60 * 5)]
    }
    query_agent = "cat /proc/uptime | awk '{ print int($1) }'"
    key = "system.uptime{0}"

    def run(self, zbx):
        uptime = open("/proc/uptime", "r").read().split(" ")[0]
        zbx.send("system.uptime[]", int(float(uptime)))

    def items(self, template, dashboard=False):
        if not dashboard:
            return template.item({
                "name": "System: Uptime",
                "key": self.right_type(self.key),
                "value_type": Plugin.VALUE_TYPE.numeric_unsigned,
                "delay": self.plugin_config("interval"),
                "units": Plugin.UNITS.uptime
            })
        else:
            return []

    def macros(self, template, dashboard=False):
        result = ""
        for macro in self.plugin_macros.keys():
            result += template.mamonsu_macro(defaults=self.plugin_macros[macro])
        if not dashboard:
            return result
        else:
            return []

    def triggers(self, template, dashboard=False):
        return template.trigger(
            {
                "name": "System: {HOSTNAME} was restarted (start time={ITEM.LASTVALUE})",
                "expression": "{#TEMPLATE:" + self.right_type(self.key) + ".last()}&lt;" + self.plugin_macros["system_uptime"][0][1]
            }
        )

    # TODO: define another metric key because it duplicates native zabbix agents keys
    # def keys_and_queries(self, template_zabbix):
    #     result = ["system.uptime,{0}".format(self.query_agent)]
    #     return template_zabbix.key_and_query(result)
