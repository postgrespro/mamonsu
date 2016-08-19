from mamonsu.plugins.system.plugin import SystemPlugin as Plugin


class Memory(Plugin):

    # colors
    # 1. physical memory
    # 2. virtual memory

    Items = [
        # zbx_key, meminfo_key, name, color
        ('apps', None,
            'Apps: User-space applications', 'CC0000'),

        ('buffers', 'Buffers',
            'Buffers: Block device cache and dirty', '00CC00'),

        ('swap', None,
            'Swap: Swap space used', '0000CC'),

        ('cached', 'Cached',
            'Cached: Parked file data (file content) cache', 'CC00CC'),

        ('unused', 'MemFree',
            'Free: Wasted memory', '000000'),

        ('slab', 'Slab',
            'Slab: Kernel used memory (inode cache)', 'CCCC00'),

        ('swap_cache', 'SwapCached',
            'SwapCached: Fetched unmod yet swap pages', '777777'),

        ('page_tables', 'PageTables',
            'PageTables: Map bt virtual and physical', '770000'),

        ('vmalloc_used', 'VmallocUsed',
            'VMallocUsed: vmaloc() allocated by kernel', '000077'),

        ('committed', 'Committed_AS',
            'Committed_AS: Total committed memory', '007700'),

        ('mapped', 'Mapped',
            'Mapped: All mmap()ed pages', 'DF0000'),

        ('active', 'Active',
            'Active: Memory recently used', '00DF00'),

        ('inactive', 'Inactive',
            'Inactive: Memory not currently used', '0000DF')
    ]

    def run(self, zbx):

        meminfo, result = {}, {}

        with open('/proc/meminfo', 'r') as f:
            for line in f:
                data = line.split()
                key, val = data[0], data[1]
                key = key.split(':')[0]
                meminfo[key] = float(val) * 1024

        for item in self.Items:
            zbx_key, meminfo_key = item[0], item[1]
            if meminfo_key is not None:
                result[zbx_key] = meminfo.get(meminfo_key) or 0
        result['apps'] = meminfo['MemTotal'] - result['unused'] \
            - result['buffers'] - result['cached'] - result['slab'] \
            - result['page_tables'] - result['swap_cache']
        result['swap'] = (meminfo.get('SwapTotal') or 0) \
            - (meminfo.get('SwapFree') or 0)

        for key in result:
            zbx.send('system.memory[{0}]'.format(key), result[key])

        del result, meminfo

    def items(self, template):
        result = ''
        for item in self.Items:
            result += template.item({
                'name': '{0}'.format(item[2]),
                'key': 'system.memory[{0}]'.format(item[0]),
                'units': 'b'
            })
        return result

    def graphs(self, template):
        items = []
        for item in self.Items:
            items.append({
                'key': 'system.memory[{0}]'.format(item[0]),
                'color': item[3]
            })
        graph = {
            'name': 'Memory overview', 'height': 400,
            'type': 1, 'items': items}
        return template.graph(graph)
