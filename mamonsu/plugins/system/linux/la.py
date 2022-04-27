from mamonsu.plugins.system.plugin import SystemPlugin as Plugin


class La(Plugin):
    AgentPluginType = "system"

    query_agent = "cat /proc/loadavg | awk '{ print $1 }'"
    key = "system.la{0}"

    def run(self, zbx):
        la_1 = open("/proc/loadavg", "r").read().split(' ')[0]
        zbx.send("system.la[1]", float(la_1))

    def items(self, template, dashboard=False):
        if not dashboard:
            return template.item({
                "name": "System: Load Average Over 1 Minute",
                "key": self.right_type(self.key, var='1'),
                "delay": self.plugin_config('interval')
            })
        else:
            return []

    def keys_and_queries(self, template_zabbix):
        result = ["system.la.1,{0}".format(self.query_agent)]
        return template_zabbix.key_and_query(result)
