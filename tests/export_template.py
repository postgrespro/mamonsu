#!/usr/bin/python

import os
import json
import urllib2

# env vars
zbx_user = os.environ.get('ZABBIX_USER') or 'Admin'
zbx_passwd = os.environ.get('ZABBIX_PASSWD') or 'zabbix'
zbx_template = os.environ.get('ZABBIX_TEMPLATE')
if zbx_template is None:
    raise Exception('Template not found')
zbx_template_name = os.environ.get('ZABBIX_TEMPLATE_NAME') or \
    'PostgresPro2-Linux'
zabbix_url = os.environ.get('ZABBIX_URL') or \
    'http://localhost/zabbix/api_jsonrpc.php'
zbx_client_host = os.environ.get('ZABBIX_CLIENT_HOST') or \
    'zbx_client_host'


def post(json_data):
    req = urllib2.Request(zabbix_url)
    req.add_header('Content-Type', 'application/json')
    response = urllib2.urlopen(req, json.dumps(json_data))
    if response.code == 200:
        body = response.read()
    else:
        raise Exception('Response code: {0}'.format(response.code))
    print('zabbix response: {0}'.format(body))
    data = json.loads(body)
    if 'error' in data:
        raise Exception('Error response from zabbix api: {0}'.format(
            data['error']))
    return data['result']

# auth
auth_data = {
    'jsonrpc': '2.0',
    'method': 'user.login',
    'params': {
        'user': zbx_user,
        'password': zbx_passwd
    },
    'id': 1
}
auth = post(auth_data)

# export
template_data = {
    'jsonrpc': '2.0',
    'method': 'configuration.import',
    'params': {
        'format': 'xml',
        'rules': {
            'templates': {
                'createMissing': True,
                'updateExisting': True
            }
        },
        'source': open(zbx_template).read(),
    },
    'auth': auth,
    'id': 1
}
if post(template_data) is not True:
    raise Exception('Export template error')

# found template
template_found = {
    'jsonrpc': '2.0',
    'method': 'template.get',
    'params': {
        'output': 'extend',
        'filter': {
            'host': [zbx_template_name]
        }
    },
    'auth': auth,
    'id': 1
}
template = None
for x in post(template_found):
    if x['name'] == zbx_template_name:
        template = int(x['templateid'])
if template is None:
    raise Exception('Template not found')

# create host
host_data = {
    "jsonrpc": '2.0',
    'method': 'host.create',
    'params': {
        'host': zbx_client_host,
        'interfaces': [
            {
                'type': 1,
                'main': 1,
                'useip': 1,
                'ip': '127.0.0.1',
                'dns': zbx_client_host,
                'port': '10050'
            }
        ],
        'groups': [{'groupid': '2'}],  # see zabbix_sql/data.sql
        'templates': [{'templateid': template}],
    },
    'auth': auth,
    'id': 1
}
host = None
for x in post(host_data)['hostids']:
    host = int(x)
print(host)
