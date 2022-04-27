from mamonsu.plugins.system.plugin import SystemPlugin as Plugin
from mamonsu.lib.zbx_template import ZbxTemplate


class Memory(Plugin):
    AgentPluginType = "system"

    query_agent = "cat /proc/meminfo | awk '/^{0}\:/ "
    query_agent_used = "MemTotal=$(cat /proc/meminfo | awk '/MemTotal\:/ { print $2 }'); " \
                       "SUM=$(cat /proc/meminfo | awk '/(MemFree|Buffers|(Swap)?Cached|Slab|PageTables)\:/ " \
                       "{ SUM += $2 } END {print SUM}'); echo $((($MemTotal-$SUM)*1024))"
    query_agent_swap = "expr `grep -Ei 'Swap(Total|Free)' /proc/meminfo | awk '{print $2 * 1024}' | paste -s -d '-' " \
                       "| sed -E 's/-/ - /g'` "
    key = "system.memory{0}"

    # colors
    # 1. physical memory
    # 2. virtual memory

    Items = [
        # zbx_key, meminfo_key, name, color, drawtype
        ("active", "Active", "Active - Memory Recently Used", "90BD72", 1),
        ("available", "MemAvailable", "Available - Free Memory", "578159", 1),
        ("buffers", "Buffers", "Buffers - Block Device Cache and Dirty", "00B0B8", 1),
        ("cached", "Cached", "Cached - Parked File Data (file content) Cache", "9C8A4E", 1),
        ("committed", "Committed_AS", "Committed AS - Total Committed Memory", "52768F", 1),
        ("inactive", "Inactive", "Inactive - Memory Not Currently Used", "001219", 1),
        ("mapped", "Mapped", "Mapped - All mmap()ed Pages", "9F1E28", 1),
        ("page_tables", "PageTables", "PageTables - Map bt Virtual and Physical", "8B817C", 1),
        ("slab", "Slab", "Slab - Kernel Used Memory (inode cache)", "F6CB93", 1),
        ("swap", None, "Swap - Swap Space Used", "0082A5", 1),
        ("swap_cache", "SwapCached", "SwapCached - Fetched unmod Yet Swap Pages", "7EB29B", 1),
        ("total", "MemTotal", "Total - All Memory", "E57862", 4),
        ("unused", "MemFree", "Unused - Wasted Memory", "3B415A", 1),
        ("used", None, "Used - User-Space Applications", "793F5D", 1),
        ("vmalloc_used", "VmallocUsed", "VMallocUsed - vmaloc() Allocated by Kernel", "CF6518", 1)
    ]

    def run(self, zbx):

        meminfo, result = {}, {}

        with open("/proc/meminfo", "r") as f:
            for line in f:
                data = line.split()
                key, val = data[0], data[1]
                key = key.split(":")[0]
                meminfo[key] = int(val) * 1024

        for item in self.Items:
            zbx_key, meminfo_key = item[0], item[1]
            if meminfo_key is not None:
                result[zbx_key] = meminfo.get(meminfo_key) or 0
        result["used"] = meminfo["MemTotal"] - result["unused"] - result["buffers"] - result["cached"] - result[
            "slab"] - result["page_tables"] - result["swap_cache"]
        result["swap"] = (meminfo.get("SwapTotal") or 0) - (meminfo.get("SwapFree") or 0)

        for key in result:
            zbx.send("system.memory[{0}]".format(key), result[key])

        del result, meminfo

    def items(self, template, dashboard=False):
        result = ""
        for item in self.Items:
            result += template.item({
                "name": "System: {0}".format(item[2]),
                "key": self.right_type(self.key, item[0]),
                "units": Plugin.UNITS.bytes,
                "delay": self.plugin_config("interval"),
                "value_type": Plugin.VALUE_TYPE.numeric_unsigned
            })
        if not dashboard:
            return result
        else:
            return []

    def graphs(self, template, dashboard=False):
        result = ""
        all_items = []
        free_used_items = []
        for item in self.Items:
            all_items.append({
                "key": self.right_type(self.key, item[0]),
                "color": item[3]
            })
            if item[0] in ["cached", "available", "used", "total"]:
                free_used_items.append({
                    "key": self.right_type(self.key, item[0]),
                    "color": item[3],
                    "drawtype": item[4]
                })
        graphs = [
            {
                "name": "System: Server Memory Detailed Overview",
                "height": 400,
                "type": 1,
                "items": all_items
            },
            {
                "name": "System: Server Free/Used Memory Overview",
                "height": 400,
                "type": 1,
                "items": free_used_items
            }
        ]
        if not dashboard:
            for graph in graphs:
                result += template.graph(graph)
            return result
        else:
            return [
                {
                    "dashboard": {
                        "name": "System: Server Free/Used Memory Overview",
                        "page": ZbxTemplate.dashboard_page_overview["name"],
                        "size": ZbxTemplate.dashboard_widget_size_medium,
                        "position": 4
                    }
                }
            ]

    def keys_and_queries(self, template_zabbix):
        result = []
        for item in self.Items:
            if item[1] is None and item[0] == "used":
                result.append("{0},{1}".format(self.key.format("." + item[0]), self.query_agent_used))
            elif item[1] is None and item[0] == "swap":
                result.append("{0},{1}".format(self.key.format("." + item[0]), self.query_agent_swap))
            else:
                result.append("{0},{1}{2}".format(self.key.format("." + item[0]), self.query_agent.format(item[1]),
                                                  "{ print $2*1024 }'"))
        return template_zabbix.key_and_query(result)
