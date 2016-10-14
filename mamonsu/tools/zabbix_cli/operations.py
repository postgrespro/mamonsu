# -*- coding: utf-8 -*-

import sys
import json
from mamonsu.tools.zabbix_cli.request import Request


class Operations(object):

    _help_msg = """
Arguments must be:

mamonsu zabbix template list
mamonsu zabbix template show <template name>
mamonsu zabbix template id <template name>
mamonsu zabbix template delete <template id>
mamonsu zabbix template export <file>

mamonsu zabbix host list
mamonsu zabbix host show <host name>
mamonsu zabbix host id <host name>
mamonsu zabbix host delete <host id>
mamonsu zabbix host create <host name> <hostgroup id> <template id> <ip>
mamonsu zabbix host info templates <host id>
mamonsu zabbix host info hostgroups <host id>
mamonsu zabbix host info graphs <host id>
mamonsu zabbix host info items <host id>

mamonsu zabbix hostgroup list
mamonsu zabbix hostgroup show <hostgroup name>
mamonsu zabbix hostgroup id <hostgroup name>
mamonsu zabbix hostgroup delete <hostgroup id>
mamonsu zabbix hostgroup create <hostgroup name>

mamonsu zabbix item error <host name>
mamonsu zabbix item lastvalue <host name>
mamonsu zabbix item lastclock <host name>
"""

    def __init__(self, arg):

        self.arg = arg
        if len(self.arg.commands) < 2:
            self._print_help()

        self.req = Request(
            url='{0}/api_jsonrpc.php'.format(arg.zabbix_url),
            user=arg.zabbix_user,
            passwd=arg.zabbix_password)

        if self.arg.commands[0] == 'template':
            return self.template(self.arg.commands[1:])
        elif self.arg.commands[0] == 'hostgroup':
            return self.hostgroup(self.arg.commands[1:])
        elif self.arg.commands[0] == 'host':
            return self.host(self.arg.commands[1:])
        elif self.arg.commands[0] == 'item':
            return self.item(self.arg.commands[1:])
        else:
            self._print_help()

    def _print_help(self):
        sys.stderr.write(self._help_msg)
        sys.exit(1)

    def _generic_delete(self, typ, ids):
        if typ == 'template':
            params = [ids]
        elif typ == 'hostgroup':
            params = [ids]
        elif typ == 'host':
            params = [ids]
        else:
            sys.stderr.write('Unknown type: {0} for deleting'.format(typ))
            sys.exit(4)
        try:
            print(self.req.post(
                method='{0}.delete'.format(typ),
                params=params))
        except Exception as e:
            sys.stderr.write('List error: {0}\n'.format(e))
            sys.exit(3)

    def _generic_list(self, typ):
        if typ == 'template':
            name, fltr = 'name', 'host'
        elif typ == 'hostgroup':
            name, fltr = 'name', 'host'
        elif typ == 'host':
            fltr, name = 'host', 'host'
        else:
            sys.stderr.write('Unknown type: {0} for listing'.format(typ))
            sys.exit(4)
        try:
            for x in self.req.post(
                method='{0}.get'.format(typ),
                params={
                    'filter': {fltr: []}}):
                print(x[name])
        except Exception as e:
            sys.stderr.write('List error: {0}\n'.format(e))
            sys.exit(3)

    def _generic_show(self, typ, name, onlyid=False):
        if typ == 'template':
            fltr, ids = {'host': [name]}, 'templateid'
        elif typ == 'hostgroup':
            fltr, ids = {'name': [name]}, 'groupid'
        elif typ == 'host':
            fltr, ids = {'host': [name]}, 'hostid'
        else:
            sys.stderr.write('Unknown type: {0} for showing'.format(typ))
            sys.exit(4)
        try:
            x = self.req.post(
                method='{0}.get'.format(typ),
                params={'filter': fltr})
            if len(x) == 0:
                sys.stderr.write('{0} not found!\n'.format(name))
                sys.exit(2)
            if len(x) > 1:
                sys.stderr.write(
                    'Too many found: {0}\n'.format(x))
                sys.exit(2)
            if onlyid:
                print(x[0][ids])
            else:
                print(json.dumps(x[0], indent=2))
        except Exception as e:
            sys.stderr.write('Show error: {0}\n'.format(e))
            sys.exit(3)

    def _use_generic(self, args, typ):
        if args[0] == 'list':
            self._generic_list(typ)
            return True
        elif args[0] == 'show':
            if not len(args) == 2:
                return self._print_help()
            self._generic_show(typ, args[1])
            return True
        elif args[0] == 'id':
            if not len(args) == 2:
                return self._print_help()
            self._generic_show(typ, args[1], onlyid=True)
            return True
        elif args[0] == 'delete':
            if not len(args) == 2:
                return self._print_help()
            self._generic_delete(typ, args[1])
            return True
        else:
            return False

    def template(self, args):

        if self._use_generic(args, 'template'):
            return

        if args[0] == 'export':
            if not len(args) == 2:
                return self._print_help()
            file = args[1]
            try:
                if not self.req.post(
                    method='configuration.import',
                    params={
                        'format': 'xml',
                        'rules': {
                        'templates': {
                            'createMissing': True,
                            'updateExisting': True},
                        'applications': {
                            'createMissing': True,
                            'updateExisting': True},
                        'discoveryRules': {
                            'createMissing': True,
                            'updateExisting': True},
                        'graphs': {
                            'createMissing': True,
                            'updateExisting': True},
                        'items': {
                            'createMissing': True,
                            'updateExisting': True},
                        'triggers': {
                            'createMissing': True,
                            'updateExisting': True},
                        },
                        'source': open(file).read()}):
                    raise Exception('Export template error')
            except Exception as e:
                sys.stderr.write('Template export error: {0}\n'.format(e))
                sys.exit(3)
            return

        return self._print_help()

    def hostgroup(self, args):

        if self._use_generic(args, 'hostgroup'):
            return

        if args[0] == 'create':
            if not len(args) == 2:
                return self._print_help()
            name = args[1]
            try:
                result = self.req.post(
                    method='hostgroup.create',
                    params={'name': name})
                print(result['groupids'][0])
            except Exception as e:
                sys.stderr.write('Hostgroup create error: {0}\n'.format(e))
                sys.exit(3)
            finally:
                return

        return self._print_help()

    def host(self, args):

        def _extented_info(self, hostid, key, val):
            data = self.req.post(
                method='host.get',
                params={
                    'output': ['host'],
                    'hostids': hostid,
                    key: val
                })
            if not len(data) == 1:
                if len(data) == 0:
                    sys.stderr.write('Host not found: {0}\n'.format(hostid))
                else:
                    sys.stderr.write(
                        'Too many hosts found: {0}\n'.format(data))
                sys.exit(4)
            print(json.dumps(data[0], indent=2))

        if args[0] == 'info':
            if not len(args) == 3:
                return self._print_help()
            try:
                if args[1] == 'templates':
                    return _extented_info(
                        self, args[2],
                        'selectParentTemplates', ['templateid', 'name'])
                elif args[1] == 'hostgroups':
                    return _extented_info(
                        self, args[2],
                        'selectGroups', ['groupid', 'name'])
                elif args[1] == 'items':
                    return _extented_info(
                        self, args[2],
                        'selectItems', ['_key'])
                elif args[1] == 'graphs':
                    return _extented_info(
                        self, args[2],
                        'selectGraphs', ['graphid', 'name'])
                else:
                    self._print_help()
            except Exception as e:
                sys.stderr.write('Found error: {0}\n'.format(e))
                sys.exit(4)
            finally:
                return

        if self._use_generic(args, 'host'):
            return

        if args[0] == 'create':
            if not len(args) == 5:
                return self._print_help()
            name, groupid, templateid, ip = args[1], args[2], args[3], args[4]
            try:
                print(self.req.post(
                    method='host.create',
                    params={
                        'host': name,
                        'interfaces': [{
                            'type': 1, 'main': 1, 'useip': 1,
                            'ip': ip, 'dns': '', 'port': '10050'}],
                        'groups': [{'groupid': groupid}],
                        'templates': [{'templateid': templateid}]
                    }))
            except Exception as e:
                sys.stderr.write('Host create error: {0}\n'.format(e))
                sys.exit(4)
            finally:
                return

        return self._print_help()

    def item(self, args):
        if len(args) != 2:
            return self._print_help()
        typ, hostname = args[0], args[1]
        try:
            hosts = self.req.post('host.get', {'filter': {'host': [hostname]}})
            if len(hosts) == 0:
                sys.stderr.write('{0} not found!\n'.format(hostname))
                sys.exit(2)
            if len(hosts) > 1:
                sys.stderr.write('Too many found for {0}!\n'.format(hostname))
                sys.exit(2)
            host_id = hosts[0]['hostid']
            for item in self.req.post('item.get', {'hostids': [host_id]}):
                if typ == 'error':
                    if item['error'] == '':
                        continue
                print('{0}\t{1}'.format(
                    item['key_'],
                    item[typ]))
        except Exception as e:
            sys.stderr.write('Error find: {0}\n'.format(e))
            sys.exit(3)
