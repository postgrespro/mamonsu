import os
from mamonsu.lib.plugin import Plugin


class DiskSizes(Plugin):

    ExcludeFsTypes = [
        'none', 'unknown', 'rootfs', 'iso9660',
        'squashfs', 'udf', 'romfs', 'ramfs',
        'debugfs', 'cgroup', 'cgroup_root',
        'pstore', 'devtmpfs', 'autofs',
        'cgroup', 'configfs', 'devpts',
        'efivarfs', 'fusectl', 'fuse.gvfsd-fuse',
        'hugetlbfs', 'mqueue',
        'nfsd', 'proc', 'pstore',
        'rpc_pipefs', 'securityfs', 'sysfs',
        'nsfs', 'tmpfs', 'tracefs']

    def __init__(self, config):
        super(DiskSizes, self).__init__(config)
        self.TriggerPfreeLessThen = self.config.fetch(
            'disk_sizes', 'percent_free', int)
        self.TriggerPIfreeLessThen = self.config.fetch(
            'disk_sizes', 'inode_percent_free', int)

    def run(self, zbx):
        with open('/proc/self/mountinfo', 'r') as f:

            points = []

            for line in f:
                data = line.split()
                if len(data) != 11:
                    continue
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
                    (vfs.f_blocks - vfs.f_bfree) * vfs.f_bsize)
                zbx.send(
                    'system.vfs.free[{0}]'.format(point),
                    vfs.f_bfree * vfs.f_bsize)
                zbx.send(
                    'system.vfs.percent_free[{0}]'.format(point),
                    100 - (float(vfs.f_blocks - vfs.f_bfree)*100/vfs.f_blocks))
                zbx.send(
                    'system.vfs.percent_inode_free[{0}]'.format(point),
                    100 - (float(vfs.f_files - vfs.f_ffree)*100/vfs.f_files))

            zbx.send('system.vfs.discovery[]', zbx.json({'data': points}))

    def discovery_rules(self, template):

        rule = {
            'name': 'VFS discovery',
            'key': 'system.vfs.discovery[]',
            'filter': '{#MOUNTPOINT}:.*'
        }

        items = [
            {
                'key': 'system.vfs.used[{#MOUNTPOINT}]',
                'name': 'Mount point {#MOUNTPOINT}: used',
                'units': Plugin.UNITS.bytes},
            {
                'key': 'system.vfs.free[{#MOUNTPOINT}]',
                'name': 'Mount point {#MOUNTPOINT}: free',
                'units': Plugin.UNITS.bytes},
            {
                'key': 'system.vfs.percent_free[{#MOUNTPOINT}]',
                'name': 'Mount point {#MOUNTPOINT}: free in percents',
                'units': Plugin.UNITS.percent},
            {
                'key': 'system.vfs.percent_inode_free[{#MOUNTPOINT}]',
                'name': 'Mount point {#MOUNTPOINT}: free inodes in percent',
                'units': Plugin.UNITS.percent}]

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
            '()}&lt;' + str(self.TriggerPfreeLessThen)},
            {
            'name': 'Free inode space less then 10% on mountpoint '
            '{#MOUNTPOINT} (hostname={HOSTNAME} value={ITEM.LASTVALUE})',
            'expression': '{#TEMPLATE:system.vfs.'
            'percent_inode_free[{#MOUNTPOINT}].last'
            '()}&lt;' + str(self.TriggerPIfreeLessThen)
        }]

        return template.discovery_rule(
            rule=rule, items=items, graphs=graphs, triggers=triggers)
