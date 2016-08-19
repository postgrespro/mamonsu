from .helpers import DiskInfo, PerfData

from mamonsu.plugins.system.plugin import SystemPlugin as Plugin


class DiskStats(Plugin):

    def run(self, zbx):
        devices = []
        for disk in DiskInfo.get_fixed_drivers():
            perf_services = [
                r'\LogicalDisk({0}:)\Disk Reads/sec'.format(disk),
                r'\LogicalDisk({0}:)\Disk Writes/sec'.format(disk),
                r'\LogicalDisk({0}:)\% Idle Time'.format(disk),
                r'\LogicalDisk({0}:)\Avg. Disk Queue Length'.format(disk)]
            data = PerfData.get(perf_services, delay=1000)
            zbx.send('system.disk.read[{0}]'.format(disk), float(data[0]))
            zbx.send('system.disk.write[{0}]'.format(disk), float(data[1]))
            zbx.send('system.disk.idle[{0}]'.format(disk), float(data[2]))
            zbx.send('system.disk.queue_avg[{0}]'.format(disk), float(data[3]))
            devices.append({'{#LOGICALDEVICE}': disk})
            del perf_services, data
        zbx.send('system.disk.discovery[]', zbx.json({'data': devices}))
        del devices

    def discovery_rules(self, template):
        rule = {
            'name': 'Logical disks discovery',
            'key': 'system.disk.discovery[]',
            'filter': '{#LOGICALDEVICE}:.*'
        }
        items = [
            {
                'key': 'system.disk.read[{#LOGICALDEVICE}]',
                'name': 'Logical device {#LOGICALDEVICE}: read op/sec',
                'delta': Plugin.DELTA.speed_per_second},
            {
                'key': 'system.disk.write[{#LOGICALDEVICE}]',
                'name': 'Logical device {#LOGICALDEVICE}: write op/sec',
                'delta': Plugin.DELTA.speed_per_second},
            {
                'key': 'system.disk.queue_avg[{#LOGICALDEVICE}]',
                'name': 'Logical device {#LOGICALDEVICE}: queue'},
            {
                'key': 'system.disk.idle[{#LOGICALDEVICE}]',
                'name': 'Logical device {#LOGICALDEVICE}: idle time (%)',
                'units': Plugin.UNITS.percent}]
        graphs = [{
            'name': 'Logical devices overview: {#LOGICALDEVICE}',
            'items': [{
                    'color': 'CC0000',
                    'key': 'system.disk.read[{#LOGICALDEVICE}]'},
                {
                    'color': '0000CC',
                    'key': 'system.disk.write[{#LOGICALDEVICE}]'},
                {
                    'key': 'system.disk.queue_avg[{#LOGICALDEVICE}]',
                    'name': 'Logical device {#LOGICALDEVICE}: queue',
                    'yaxisside': 1}]
        }]
        return template.discovery_rule(rule=rule, items=items, graphs=graphs)
