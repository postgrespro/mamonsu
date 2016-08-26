# -*- coding: utf-8 -*-

import sys
import json
from mamonsu.zabbix_tools.request import Request


class Operations(object):

    _help_msg = """
Arguments must be:

mamonsu zabbix template list
mamonsu zabbix template export <file>
mamonsu zabbix template show <template name>
mamonsu zabbix template id <template name>

mamonsu zabbix hostgroup list
mamonsu zabbix hostgroup create <hostgroup name>
mamonsu zabbix hostgroup delete <hostgroup id>
mamonsu zabbix hostgroup show <hostgroup name>
mamonsu zabbix hostgroup id <hostgroup name>

mamonsu zabbix host list
mamonsu zabbix host create <host name> <hostgroup id> <template id> <ip>
mamonsu zabbix host show <hostname>
mamonsu zabbix host id <hostname>
"""

    def __init__(self, arg):

        self.arg = arg
        if len(self.arg.arguments) < 2:
            self._print_help()

        self.req = Request(
            url='{0}/api_jsonrpc.php'.format(arg.zabbix_url),
            user=arg.zabbix_user,
            passwd=arg.zabbix_password)

        if self.arg.arguments[0] == 'template':
            return self.template(self.arg.arguments[1:])

        if self.arg.arguments[0] == 'hostgroup':
            return self.hostgroup(self.arg.arguments[1:])

        if self.arg.arguments[0] == 'host':
            return self.host(self.arg.arguments[1:])

        self._print_help()

    def _print_help(self):
        sys.stderr.write(self._help_msg)
        sys.exit(1)

    def _generic_list(self, typ):
        method = 'unknown'
        fltr = {}
        name = 'name'
        if typ == 'template':
            method = 'template.get'
            fltr = {'host': []}
        if typ == 'hostgroup':
            method = 'hostgroup.get'
            fltr = {'name': []}
        if typ == 'host':
            method = 'host.get'
            fltr = {'host': []}
            name = 'host'
        try:
            for x in self.req.post(
                method=method,
                params={
                    'filter': fltr}):
                print x[name]
        except Exception as e:
            sys.stderr.write('List error {0}\n'.format(e))

    def _generic_show(self, typ, name, onlyid=False):
        method = 'unknown'
        fltr = {}
        ids = 'unknown'
        if typ == 'template':
            method = 'template.get'
            fltr = {'host': [name]}
            ids = 'templateid'
        if typ == 'hostgroup':
            method = 'hostgroup.get'
            fltr = {'name': [name]}
            ids = 'groupid'
        if typ == 'host':
            method = 'host.get'
            fltr = {'output': 'extend', 'host': [name]}
            ids = 'hostid'
        try:
            x = self.req.post(
                method=method,
                params={'filter': fltr})
            if len(x) == 0:
                sys.stderr.write('{0} not found!\n'.format(name))
                sys.exit(2)
            if len(x) > 1:
                sys.stderr.write(
                    'Found too many: {0}\n'.format(x))
                sys.exit(2)
            if onlyid:
                print(x[0][ids])
            else:
                print(json.dumps(x[0], indent=2))
        except Exception as e:
            sys.stderr.write('show error {0}\n'.format(e))

    def template(self, args):

        if args[0] == 'list':
            return self._generic_list('template')

        if args[0] == 'show':
            if not len(args) == 2:
                return self._print_help()
            return self._generic_show('template', args[1])

        if args[0] == 'id':
            if not len(args) == 2:
                return self._print_help()
            return self._generic_show('template', args[1], onlyid=True)

        if args[0] == 'export':
            if not len(args) == 2:
                return self._print_help()
            file = args[1]
            try:
                if not self.req.post(
                    method='configuration.import',
                    params={
                        'format': 'xml',
                        'rules': {'templates': {
                                    'createMissing': True,
                                    'updateExisting': True}},
                        'source': open(file).read()}):
                    raise Exception('Export template error')
            except Exception as e:
                sys.stderr.write('Template export error {0}\n'.format(e))
            finally:
                return

        return self._print_help()

    def hostgroup(self, args):

        if args[0] == 'list':
            return self._generic_list('hostgroup')

        if args[0] == 'show':
            if not len(args) == 2:
                return self._print_help()
            return self._generic_show('hostgroup', args[1])

        if args[0] == 'id':
            if not len(args) == 2:
                return self._print_help()
            return self._generic_show('hostgroup', args[1], onlyid=True)

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
                sys.stderr.write('Hostgroup create error {0}\n'.format(e))
            finally:
                return

        if args[0] == 'del' or args[0] == 'delete':
            if not len(args) == 2:
                return self._print_help()
            ids = args[1]
            try:
                print(self.req.post(
                    method='hostgroup.delete',
                    params=[ids]))
            except Exception as e:
                sys.stderr.write('Hostgroup delete error {0}\n'.format(e))
            finally:
                return

        return self._print_help()

    def host(self, args):

        if args[0] == 'list':
            return self._generic_list('host')

        if args[0] == 'show':
            if not len(args) == 2:
                return self._print_help()
            return self._generic_show('host', args[1])

        if args[0] == 'id':
            if not len(args) == 2:
                return self._print_help()
            return self._generic_show('host', args[1], onlyid=True)

        if args[0] == 'create':
            if not len(args) == 5:
                return self._print_help()
            name, groupid, templateid, ip = args[1], args[2], args[3], args[4]
            try:
                print(self.req.post(
                    method='host.create',
                    params={
                        'host': name,
                        'interfaces': {
                            'type': 1, 'main': 1, 'useip': 1,
                            'ip': ip, 'dns': '', 'port': '10050'},
                        'groups': [{'groupid': groupid}],
                        'templates': [{'templateid': templateid}]
                    }))
            except Exception as e:
                sys.stderr.write('Host create error {0}\n'.format(e))
            finally:
                return

        return self._print_help()
