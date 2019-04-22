import re
from mamonsu.plugins.system.plugin import SystemPlugin as Plugin


class DiskStats(Plugin):

    # todo yaxis right 100%
    # bold line
    AgentPluginType = 'sys'
    query_agent_discovery = "/etc/zabbix/scripts/agentd/zapgix/disk_stats.sh -j $1"
    agent_query_read_op = "expr `grep -w '$1' /proc/diskstats | awk '{print $$4}'`"
    agent_query_read_sc = "expr `grep -w '$1' /proc/diskstats | awk '{print $$6 * 512}'`"
    agent_query_write_op = "expr `grep -w '$1' /proc/diskstats | awk '{print $$8}'`"
    agent_query_write_sc = "expr `grep -w '$1' /proc/diskstats | awk '{print $$10 * 512}'`"
    agent_query_ticks = "expr `grep -w '$1' /proc/diskstats | awk '{print $$13}'`"
    agent_query_read_op_all = "/etc/zabbix/scripts/agentd/zapgix/disk_stats_read_op.sh"   #    get sum for all read_op
    agent_query_read_sc_all = "/etc/zabbix/scripts/agentd/zapgix/disk_stats_read_b.sh"
    agent_query_write_op_all = "/etc/zabbix/scripts/agentd/zapgix/disk_stats_write_op.sh"
    agent_query_write_sc_all = "/etc/zabbix/scripts/agentd/zapgix/disk_stats_write_b.sh"

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
                if self.OnlyPhysicalDevices and re.search('\d+$', dev): # get drive name without digits at the end
                    continue
                val = [int(x) for x in val.split()]
                read_op, read_sc, write_op, write_sc, ticks = val[0], val[2], val[4], val[6], val[9]
                read_b, write_b = read_sc * 512, write_sc * 512  # https://github.com/sysstat/sysstat/blob/v11.5.2/iostat.c#L940

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

    def items(self, template):
        return template.item({
            'name': 'Block devices: read requests',
            'key': 'system.disk.all_read[]'
        }) + template.item({
            'name': 'Block devices: write requests',
            'key': 'system.disk.all_write[]'
        }) + template.item({
            'name': 'Block devices: read byte/s',
            'key': 'system.disk.all_read_b[]'
        }) + template.item({
            'name': 'Block devices: write byte/s',
            'key': 'system.disk.all_write_b[]'
        })

    def graphs(self, template):
        graph = {
            'name': 'Block devices: read/write operations',
            'items': [
                {'key': 'system.disk.all_read[]', 'color': 'CC0000'},
                {'key': 'system.disk.all_write[]', 'color': '0000CC'}]
        }
        result = template.graph(graph)
        graph = {
            'name': 'Block devices: read/write bytes',
            'items': [
                {'key': 'system.disk.all_read_b[]', 'color': 'CC0000'},
                {'key': 'system.disk.all_write_b[]', 'color': '0000CC'}]
        }
        return result + template.graph(graph)

    def discovery_rules(self, template):
        if Plugin.Type == 'mamonsu':
            rule = {
                'name': 'Block device discovery',
                'key': 'system.disk.discovery[BLOCKDEVICE]',
                'filter': '{#BLOCKDEVICE}:.*'
            }
        else:
            rule = {
                'name': 'Block device discovery',
                'key': 'system.disk.discovery[]',
                'filter': '{#BLOCKDEVICE}:.*'
            }

        items = [
            {
                'key': 'system.disk.utilization[{#BLOCKDEVICE}]',
                'name': 'Block device {#BLOCKDEVICE}: utilization',
                'units': Plugin.UNITS.percent},
            {
                'key': 'system.disk.read[{#BLOCKDEVICE}]',
                'name': 'Block device {#BLOCKDEVICE}: read operations'},
            {
                'key': 'system.disk.write[{#BLOCKDEVICE}]',
                'name': 'Block device {#BLOCKDEVICE}: write operations'},
            {
                'key': 'system.disk.read_b[{#BLOCKDEVICE}]',
                'name': 'Block device {#BLOCKDEVICE}: read byte/s',
                'units': Plugin.UNITS.bytes},
            {
                'key': 'system.disk.write_b[{#BLOCKDEVICE}]',
                'name': 'Block device {#BLOCKDEVICE}: write byte/s',
                'units': Plugin.UNITS.bytes}]

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

        return template.discovery_rule(rule=rule, items=items, graphs=graphs)

    def keys_and_queries(self, template_zabbix):
        result = []
        result.append('system.disk.discovery[*],{0}'.format(self.query_agent_discovery))
        result.append('system.disk.read[*],{0}'.format(self.agent_query_read_op))
        result.append('system.disk.write[*],{0}'.format(self.agent_query_write_op))
        result.append('system.disk.read_b[*],{0}'.format(self.agent_query_read_sc))
        result.append('system.disk.write_b[*],{0}'.format(self.agent_query_write_sc))
        result.append('system.disk.all_read[],{0}'.format(self.agent_query_read_op_all))
        result.append('system.disk.all_write[],{0}'.format(self.agent_query_write_op_all))
        result.append('system.disk.all_read_b[],{0}'.format(self.agent_query_read_sc_all))
        result.append('system.disk.all_write_b[],{0}'.format(self.agent_query_write_sc_all))
        return template_zabbix.key_and_query(result)

