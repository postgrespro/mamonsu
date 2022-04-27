from mamonsu.plugins.system.plugin import SystemPlugin as Plugin


class OpenFiles(Plugin):
    AgentPluginType = "system"

    query_agent = "cat  /proc/sys/fs/file-nr | awk '{ print $1 }'"
    key = "system.open_files{0}"

    def run(self, zbx):
        open_files = open("/proc/sys/fs/file-nr", "r").read().split("\t")[0]
        zbx.send("system.open_files[]", int(open_files))

    def items(self, template, dashboard=False):
        if not dashboard:
            return template.item({
                "name": "System: Opened Files",
                "key": self.right_type(self.key),
                "value_type": Plugin.VALUE_TYPE.numeric_unsigned,
                "delay": self.plugin_config("interval")
            })
        else:
            return []

    def keys_and_queries(self, template_zabbix):
        result = ["{0},{1}".format("system.open_files", self.query_agent)]
        return template_zabbix.key_and_query(result)
