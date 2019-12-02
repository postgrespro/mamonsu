from mamonsu.plugins.system.plugin import SystemPlugin as Plugin




class Net(Plugin):
    query_agent_discovery = "/net.sh -j NETDEVICE"
    query_agent = "expr `grep -Ei '$1' /proc/net/dev | awk '{print $$"
    AgentPluginType = 'sys'
    # position in line, key, desc, units
    Items = [
        (0, 'system.net.rx_bytes', 'RX bytes/s', Plugin.UNITS.bytes),
        (2, 'system.net.rx_errs', 'RX errors/s', Plugin.UNITS.none),
        (3, 'system.net.rx_drop', 'RX drops/s', Plugin.UNITS.none),
        (8, 'system.net.tx_bytes', 'TX bytes/s', Plugin.UNITS.bytes),
        (10, 'system.net.tx_errs', 'TX errors/s', Plugin.UNITS.none),
        (11, 'system.net.tx_drop', 'TX drops/s', Plugin.UNITS.none)
    ]

    def run(self, zbx):
        with open('/proc/net/dev', 'r') as f:
            devices = []
            for idx_line, line in enumerate(f, 1):
                if line.find(':') < 0 or line.find(' lo:') > 0 or idx_line < 1:
                    continue
                face, data = line.split(':')
                iface, values = face.strip(), [x for x in data.split()]
                for idx, value in enumerate(values):
                    for item in self.Items:
                        if item[0] == idx:
                            key = '{0}[{1}]'.format(item[1], iface)
                            zbx.send(key, float(value), self.DELTA_SPEED)
                devices.append({'{#NETDEVICE}': iface})
        zbx.send('system.net.discovery[]', zbx.json({'data': devices}))

    def discovery_rules(self, template):
        items = []
        if self.Type == "mamonsu":
            delta = Plugin.DELTA.as_is
            key_discovery = 'system.net.discovery[]'
        else:
            delta = Plugin.DELTA_SPEED
            key_discovery = 'system.net.discovery'
        for item in self.Items:
            items.append({
                'key': item[1] + '[{#NETDEVICE}]',
                'name': 'Network device {#NETDEVICE}: ' + item[2],
                'units': item[3],
                'delay': self.plugin_config('interval'),
                'delta': delta
            })

        rule = {
            'name': 'Net iface discovery',
            'key': key_discovery,
            'filter': '{#NETDEVICE}:.*'
        }
        graphs = [{
            'name': 'Network device: {#NETDEVICE}',
            'items': [{
                'color': 'CC0000',
                'key': 'system.net.rx_bytes[{#NETDEVICE}]'},
                {
                    'color': '0000CC',
                    'key': 'system.net.tx_bytes[{#NETDEVICE}]'}]
        }]
        return template.discovery_rule(rule=rule, items=items, graphs=graphs)

    def keys_and_queries(self, template_zabbix):
        result = []
        result.append('system.net.discovery,{0}{1}'.format(Plugin.PATH, self.query_agent_discovery))
        for item in self.Items:
            result.append('{0}[*], {1}'.format(item[1], self.query_agent + str(item[0] + 2) + "}'`"))
        return template_zabbix.key_and_query(result)
