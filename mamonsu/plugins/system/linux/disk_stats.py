import re
from mamonsu.plugins.system.plugin import SystemPlugin as Plugin
from mamonsu.lib.zbx_template import ZbxTemplate


class DiskStats(Plugin):
    # todo yaxis right 100%
    # bold line
    AgentPluginType = 'sys'
    query_agent_discovery = "/disk_stats.sh -j BLOCKDEVICE"
    agent_query_read_op = "expr `grep -w '$1' /proc/diskstats | awk '{print $$4}'`"
    agent_query_read_sc = "expr `grep -w '$1' /proc/diskstats | awk '{print $$6 * 512}'`"
    agent_query_write_op = "expr `grep -w '$1' /proc/diskstats | awk '{print $$8}'`"
    agent_query_write_sc = "expr `grep -w '$1' /proc/diskstats | awk '{print $$10 * 512}'`"
    agent_query_ticks = "expr `grep -w '$1' /proc/diskstats | awk '{print $$13 / 10}'`"
    agent_query_read_op_all = "/disk_stats_read_op.sh"  # get sum for all read_op
    agent_query_read_sc_all = "/disk_stats_read_b.sh"
    agent_query_write_op_all = "/disk_stats_write_op.sh"
    agent_query_write_sc_all = "/disk_stats_write_b.sh"

    key = 'system.disk'

    # Track only physical devices without logical partitions
    OnlyPhysicalDevices = True

    re_stat = re.compile('^(?:\s+\d+){2}\s+([\w\d]+) (.*)$')

    # rd_ios rd_merges rd_sectors rd_ticks
    # wr_ios wr_merges wr_sectors wr_ticks
    # ios_in_prog tot_ticks rq_ticks

    def run(self, zbx):
        with open('/proc/diskstats', 'r') as f:

            devices = []
            all_read_op, all_read_b, all_write_op, all_write_b, = 0, 0, 0, 0

            for line in f:
                if re.search('(ram|loop)', line):
                    continue
                m = self.re_stat.match(line)
                if m is None:
                    continue
                dev, val = m.group(1), m.group(2)
                if self.OnlyPhysicalDevices and re.search('\d+$', dev):  # get drive name without digits at the end
                    continue
                val = [int(x) for x in val.split()]
                read_op, read_sc, write_op, write_sc, ticks = val[0], val[2], val[4], val[6], val[9]
                read_b, write_b = read_sc * 512, write_sc * 512
                # https://github.com/sysstat/sysstat/blob/v11.5.2/iostat.c#L940

                zbx.send('system.disk.read[{0}]'.format(
                    dev), read_op, self.DELTA_SPEED)
                zbx.send('system.disk.write[{0}]'.format(
                    dev), write_op, self.DELTA_SPEED)
                zbx.send('system.disk.read_b[{0}]'.format(
                    dev), read_b, self.DELTA_SPEED)
                zbx.send('system.disk.write_b[{0}]'.format(
                    dev), write_b, self.DELTA_SPEED)
                zbx.send('system.disk.utilization[{0}]'.format(
                    dev), ticks / 10, self.DELTA_SPEED)

                all_read_op += read_op
                all_write_op += write_op
                all_read_b += read_b
                all_write_b += write_b
                devices.append({'{#BLOCKDEVICE}': dev})

            zbx.send('system.disk.all_read[]', all_read_op, self.DELTA_SPEED)
            zbx.send('system.disk.all_write[]', all_write_op, self.DELTA_SPEED)
            zbx.send('system.disk.all_read_b[]', all_read_b, self.DELTA_SPEED)
            zbx.send('system.disk.all_write_b[]', all_write_b, self.DELTA_SPEED)
            zbx.send('system.disk.discovery[]', zbx.json({'data': devices}))

    def items(self, template, dashboard=False):  # TODO delta speed for zabbix agent
        if Plugin.Type == "mamonsu":
            delta = Plugin.DELTA.as_is
        else:
            delta = Plugin.DELTA_SPEED
        if not dashboard:
            return template.item({
                'name': 'Block devices: read requests',
                'key': self.right_type(self.key + '.all_read{0}'),
                'delay': self.plugin_config('interval'),
                'delta': delta
            }) + template.item({
                'name': 'Block devices: write requests',
                'key': self.right_type(self.key + '.all_write{0}'),
                'delay': self.plugin_config('interval'),
                'delta': delta
            }) + template.item({
                'name': 'Block devices: read byte/s',
                'key': self.right_type(self.key + '.all_read_b{0}'),
                'delay': self.plugin_config('interval'),
                'delta': delta
            }) + template.item({
                'name': 'Block devices: write byte/s',
                'key': self.right_type(self.key + '.all_write_b{0}'),
                'delay': self.plugin_config('interval'),
                'delta': delta
            })
        else:
            return []

    def graphs(self, template, dashboard=False):
        graph = {
            'name': 'Block devices: read/write operations',
            'items': [
                {'key': self.right_type(self.key + '.all_read{0}'), 'color': 'CC0000'},
                {'key': self.right_type(self.key + '.all_write{0}'), 'color': '0000CC'}]
        }
        result = template.graph(graph)
        graph = {
            'name': 'Block devices: read/write bytes',
            'items': [
                {'key': self.right_type(self.key + '.all_read_b{0}'), 'color': 'CC0000'},
                {'key': self.right_type(self.key + '.all_write_b{0}'), 'color': '0000CC'}]
        }
        if not dashboard:
            return result + template.graph(graph)
        else:
            return [{'dashboard': {'name': 'Block devices: read/write bytes',
                                   'page': ZbxTemplate.dashboard_page_system['name'],
                                   'size': ZbxTemplate.dashboard_widget_size_medium,
                                   'position': 1}},
                    {'dashboard': {'name': 'Block devices: read/write operations',
                                   'page': ZbxTemplate.dashboard_page_system['name'],
                                   'size': ZbxTemplate.dashboard_widget_size_medium,
                                   'position': 2}}]

    def discovery_rules(self, template, dashboard=False):
        if Plugin.Type == 'mamonsu':
            key_discovery = 'system.disk.discovery[]'
            delta = Plugin.DELTA.as_is
        else:
            key_discovery = 'system.disk.discovery'
            delta = Plugin.DELTA_SPEED
        rule = {
            'name': 'Block device discovery',
            'key': key_discovery
        }
        if Plugin.old_zabbix:
            rule['filter'] = '{#BLOCKDEVICE}:.*'
            conditions = []
        else:
            conditions = [
                {
                    'condition': [
                        {'macro': '{#BLOCKDEVICE}',
                         'value': '.*',
                         'operator': 8,
                         'formulaid': 'A'}
                    ]
                }

            ]
        items = [
            {
                'key': 'system.disk.utilization[{#BLOCKDEVICE}]',
                'name': 'Block device {#BLOCKDEVICE}: utilization',
                'units': Plugin.UNITS.percent,
                'delay': self.plugin_config('interval'),
                'delta': delta},
            {
                'key': 'system.disk.read[{#BLOCKDEVICE}]',
                'name': 'Block device {#BLOCKDEVICE}: read operations',
                'delay': self.plugin_config('interval'),
                'delta': delta},
            {
                'key': 'system.disk.write[{#BLOCKDEVICE}]',
                'name': 'Block device {#BLOCKDEVICE}: write operations',
                'delay': self.plugin_config('interval'),
                'delta': delta},
            {
                'key': 'system.disk.read_b[{#BLOCKDEVICE}]',
                'name': 'Block device {#BLOCKDEVICE}: read byte/s',
                'delay': self.plugin_config('interval'),
                'units': Plugin.UNITS.bytes,
                'delta': delta},
            {
                'key': 'system.disk.write_b[{#BLOCKDEVICE}]',
                'name': 'Block device {#BLOCKDEVICE}: write byte/s',
                'delay': self.plugin_config('interval'),
                'units': Plugin.UNITS.bytes,
                'delta': delta}]

        graphs = [{
            'name': 'Block device overview: {#BLOCKDEVICE} operations',
            'items': [{
                'color': 'CC0000',
                'key': 'system.disk.read[{#BLOCKDEVICE}]'},
                {
                    'color': '0000CC',
                    'key': 'system.disk.write[{#BLOCKDEVICE}]'},
                {
                    'yaxisside': 1,
                    'color': '00CC00',
                    'key': 'system.disk.utilization[{#BLOCKDEVICE}]'}]},
            {
                'name': 'Block device overview: {#BLOCKDEVICE} byte/s',
                'items': [{
                    'color': 'CC0000',
                    'key': 'system.disk.read_b[{#BLOCKDEVICE}]'},
                    {
                        'color': '0000CC',
                        'key': 'system.disk.write_b[{#BLOCKDEVICE}]'},
                    {
                        'yaxisside': 1,
                        'color': '00CC00',
                        'key': 'system.disk.utilization[{#BLOCKDEVICE}]'}]
            }]

        return template.discovery_rule(rule=rule, conditions=conditions, items=items, graphs=graphs)

    def keys_and_queries(self, template_zabbix):
        result = ['system.disk.discovery,{0}{1}'.format(Plugin.PATH, self.query_agent_discovery),
                  'system.disk.utilization[*],{0}'.format(self.agent_query_ticks),
                  'system.disk.read[*],{0}'.format(self.agent_query_read_op),
                  'system.disk.write[*],{0}'.format(self.agent_query_write_op),
                  'system.disk.read_b[*],{0}'.format(self.agent_query_read_sc),
                  'system.disk.write_b[*],{0}'.format(self.agent_query_write_sc),
                  'system.disk.all_read,{0}{1}'.format(Plugin.PATH, self.agent_query_read_op_all),
                  'system.disk.all_write,{0}{1}'.format(Plugin.PATH, self.agent_query_write_op_all),
                  'system.disk.all_read_b,{0}{1}'.format(Plugin.PATH, self.agent_query_read_sc_all),
                  'system.disk.all_write_b,{0}{1}'.format(Plugin.PATH, self.agent_query_write_sc_all)]
        return template_zabbix.key_and_query(result)
