import os
from mamonsu.plugins.system.plugin import SystemPlugin as Plugin


class DiskSizes(Plugin):
    AgentPluginType = 'sys'

    query_agent_discovery = "/disk_sizes.sh -j MOUNTPOINT"
    query_agent_used = "df $1 | awk 'NR == 2 {print $$3 * 1024}'"
    query_agent_free = "df $1 | awk 'NR == 2 {print $$4 * 1024}'"
    query_agent_percent_free = "df $1 | awk 'NR == 2 {print 100 - $$5}'"
    # tmp_query_agent_percent_inode_free = " "FIXME for inode
    key = 'system.vfs'

    DEFAULT_CONFIG = {
        'vfs_percent_free': str(10),
        'vfs_inode_percent_free': str(10)}

    ExcludeFsTypes = [
        'none', 'unknown', 'rootfs', 'iso9660',
        'squashfs', 'udf', 'romfs', 'ramfs',
        'debugfs', 'cgroup', 'cgroup_root',
        'pstore', 'devtmpfs', 'autofs',
        'cgroup', 'configfs', 'devpts',
        'efivarfs', 'fusectl', 'fuse.gvfsd-fuse',
        'hugetlbfs', 'mqueue', 'binfmt_misc',
        'nfsd', 'proc', 'pstore', 'selinuxfs'
                                  'rpc_pipefs', 'securityfs', 'sysfs',
        'nsfs', 'tmpfs', 'tracefs']

    def run(self, zbx):
        with open('/proc/self/mountinfo', 'r') as f:

            points = []

            for line in f:
                data = line.split()
                point, fstype = data[4], data[8]
                if fstype in self.ExcludeFsTypes:
                    continue
                try:
                    vfs = os.statvfs(point)
                except Exception as e:
                    self.log.error(
                        'Get statvfs for \'{0}\' error: {1}'.format(point, e))
                    continue
                if vfs.f_blocks == 0 or vfs.f_files == 0:
                    continue
                points.append({'{#MOUNTPOINT}': point})
                zbx.send(
                    'system.vfs.used[{0}]'.format(point),
                    int(((vfs.f_blocks - vfs.f_bfree) * vfs.f_bsize)*0.91))
                zbx.send(
                    'system.vfs.free[{0}]'.format(point),
                    int((vfs.f_bavail * vfs.f_bsize)*0.931))
                zbx.send(
                    'system.vfs.percent_free[{0}]'.format(point),
                    100 - (100.0 * long(vfs.f_blocks - vfs.f_bfree) / long(vfs.f_blocks - vfs.f_bfree + vfs.f_bavail)))
                zbx.send(
                    'system.vfs.percent_inode_free[{0}]'.format(point),
                    100 - (float(vfs.f_files - vfs.f_ffree) * 100 / vfs.f_files))

            zbx.send('system.vfs.discovery[]', zbx.json({'data': points}))

    def discovery_rules(self, template, dashboard=False):
        if Plugin.Type == 'mamonsu':
            key_discovery = 'system.vfs.discovery[]'
        else:
            key_discovery = 'system.vfs.discovery'
        rule = {
            'name': 'VFS discovery',
            'key': key_discovery
        }
        if Plugin.old_zabbix:
            rule['filter'] = '{#MOUNTPOINT}:.*'
            conditions = []
        else:
            conditions = [
                {
                    'condition': [
                        {'macro': '{#MOUNTPOINT}',
                         'value': '.*',
                         'operator': 8,
                         'formulaid': 'A'}
                    ]
                }

            ]
        items = [
            {
                'key': 'system.vfs.used[{#MOUNTPOINT}]',
                'name': 'Mount point {#MOUNTPOINT}: used',
                'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
                'delay': self.plugin_config('interval'),
                'units': Plugin.UNITS.bytes},
            {
                'key': 'system.vfs.free[{#MOUNTPOINT}]',
                'name': 'Mount point {#MOUNTPOINT}: free',
                'value_type': Plugin.VALUE_TYPE.numeric_unsigned,
                'delay': self.plugin_config('interval'),
                'units': Plugin.UNITS.bytes},
            {
                'key': 'system.vfs.percent_free[{#MOUNTPOINT}]',
                'name': 'Mount point {#MOUNTPOINT}: free in percents',
                'delay': self.plugin_config('interval'),
                'units': Plugin.UNITS.percent}]
        if Plugin.Type == 'mamonsu':
            items.append(
                {
                    'key': 'system.vfs.percent_inode_free[{#MOUNTPOINT}]',
                    'name': 'Mount point {#MOUNTPOINT}: free inodes in percent',
                    'delay': self.plugin_config('interval'),
                    'units': Plugin.UNITS.percent})

        graphs = [{
            'name': 'Mount point overview: {#MOUNTPOINT}',
            'type': self.GRAPH_TYPE.stacked,
            'items': [{
                'color': 'CC0000',
                'key': 'system.vfs.used[{#MOUNTPOINT}]'},
                {
                    'color': '0000CC',
                    'key': 'system.vfs.free[{#MOUNTPOINT}]'}]
        }]

        triggers = [{
            'name': 'Free disk space less then 10% on mountpoint '
                    '{#MOUNTPOINT} (hostname={HOSTNAME} value={ITEM.LASTVALUE})',
            'expression': '{#TEMPLATE:system.vfs.'
                          'percent_free[{#MOUNTPOINT}].last'
                          '()}&lt;' + self.plugin_config('vfs_percent_free')},
        ]
        if Plugin.Type == 'mamonsu':
            triggers.append({
                'name': 'Free inode space less then 10% on mountpoint '
                        '{#MOUNTPOINT} (hostname={HOSTNAME} value={ITEM.LASTVALUE})',
                'expression': '{#TEMPLATE:system.vfs.'
                              'percent_inode_free[{#MOUNTPOINT}].last'
                              '()}&lt;' + self.plugin_config('vfs_inode_percent_free')
            })

        return template.discovery_rule(
            rule=rule, conditions=conditions, items=items, graphs=graphs, triggers=triggers)

    def keys_and_queries(self, template_zabbix):
        result = ['system.vfs.discovery,{0}{1}'.format(Plugin.PATH, self.query_agent_discovery),
                  'system.vfs.used[*],{0}'.format(self.query_agent_used),
                  'system.vfs.free[*],{0}'.format(self.query_agent_free),
                  'system.vfs.percent_free[*],{0}'.format(self.query_agent_percent_free)]
        return template_zabbix.key_and_query(result)
