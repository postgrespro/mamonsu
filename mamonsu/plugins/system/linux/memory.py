from mamonsu.plugins.system.plugin import SystemPlugin as Plugin
from mamonsu.lib.zbx_template import ZbxTemplate


class Memory(Plugin):
    AgentPluginType = 'sys'
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
        ('total', 'MemTotal', 'Memory Total', '5CA8FF', 4),
        ('used', None, 'Used: User-space applications', 'CC0000', 1),
        ('buffers', 'Buffers', 'Buffers: Block device cache and dirty', '00CC00', 1),
        ('swap', None, 'Swap: Swap space used', '0000CC', 1),
        ('cached', 'Cached', 'Cached: Parked file data (file content) cache', 'CC00CC', 1),
        ('unused', 'MemFree', 'Free: Wasted memory', '000000', 1),
        ('available', 'MemAvailable', 'Free: Available', '008000', 1),
        ('slab', 'Slab', 'Slab: Kernel used memory (inode cache)', 'CCCC00', 1),
        ('swap_cache', 'SwapCached', 'SwapCached: Fetched unmod yet swap pages', '777777', 1),
        ('page_tables', 'PageTables', 'PageTables: Map bt virtual and physical', '770000', 1),
        ('vmalloc_used', 'VmallocUsed', 'VMallocUsed: vmaloc() allocated by kernel', '000077', 1),
        ('committed', 'Committed_AS', 'Committed_AS: Total committed memory', '007700', 1),
        ('mapped', 'Mapped', 'Mapped: All mmap()ed pages', 'DF0000', 1),
        ('active', 'Active', 'Active: Memory recently used', '00DF00', 1),
        ('inactive', 'Inactive', 'Inactive: Memory not currently used', '0000DF', 1)
    ]

    def run(self, zbx):

        meminfo, result = {}, {}

        with open('/proc/meminfo', 'r') as f:
            for line in f:
                data = line.split()
                key, val = data[0], data[1]
                key = key.split(':')[0]
                meminfo[key] = int(val) * 1024

        for item in self.Items:
            zbx_key, meminfo_key = item[0], item[1]
            if meminfo_key is not None:
                result[zbx_key] = meminfo.get(meminfo_key) or 0
        result['used'] = meminfo['MemTotal'] - result['unused'] \
                         - result['buffers'] - result['cached'] - result['slab'] \
                         - result['page_tables'] - result['swap_cache']
        result['swap'] = (meminfo.get('SwapTotal') or 0) \
                         - (meminfo.get('SwapFree') or 0)

        for key in result:
            zbx.send('system.memory[{0}]'.format(key), result[key])

        del result, meminfo

    def items(self, template, dashboard=False):
        result = ''
        for item in self.Items:
            result += template.item({
                'name': '{0}'.format(item[2]),
                'key': self.right_type(self.key, item[0]),
                'units': Plugin.UNITS.bytes,
                'delay': self.plugin_config('interval'),
                'value_type': Plugin.VALUE_TYPE.numeric_unsigned
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
                'key': self.right_type(self.key, item[0]),
                'color': item[3]
            })
            if item[0] in ['cached', 'available', 'used', 'total']:
                free_used_items.append({
                    'key': self.right_type(self.key, item[0]),
                    'color': item[3],
                    'drawtype': item[4]
                })
        graphs = [{'name': 'Server Memory Detailed Overview',
                   'height': 400,
                   'type': 1,
                   'items': all_items},
                  {'name': 'Server Free/Used Memory Overview',
                   'height': 400,
                   'type': 0,
                   'items': free_used_items}
                  ]
        if not dashboard:
            for graph in graphs:
                result += template.graph(graph)
            return result
        else:
            return [{'dashboard': {'name': 'Server Memory Detailed Overview',
                                   'page': ZbxTemplate.dashboard_page_overview['name'],
                                   'size': ZbxTemplate.dashboard_widget_size_medium,
                                   'position': 4}}]

    def keys_and_queries(self, template_zabbix):
        result = []
        for item in self.Items:
            if item[1] is None and item[0] == 'used':
                result.append('{0},{1}'.format(self.key.format('.' + item[0]),
                                               self.query_agent_used))
            elif item[1] is None and item[0] == 'swap':
                result.append('{0},{1}'.format(self.key.format('.' + item[0]),
                                               self.query_agent_swap))
            else:
                result.append('{0},{1}{2}'.format(self.key.format('.' + item[0]),
                                                  self.query_agent.format(item[1]), "{ print $2*1024 }'"))
        return template_zabbix.key_and_query(result)
