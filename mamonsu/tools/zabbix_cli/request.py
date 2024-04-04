# -*- coding: utf-8 -*-

import json
import logging
from collections import OrderedDict


from distutils.version import LooseVersion
import urllib.request as urllib2


class Request(object):

    def __init__(self, url, user, passwd):
        self._url, self._user, self._passwd = url, user, passwd
        self._id, self._auth_tocken = 0, None
        self._api_version = self.post(method='apiinfo.version', params=[])

    def set_user(self, user):
        self._user=user

    def set_passwd(self, passwd):
        self._passwd=passwd

    def _auth(self):
        if self._auth_tocken is None:
            if not self._user:
                return None
            user_field = 'user' if LooseVersion(self._api_version) < LooseVersion('6.4') else 'username'
            self._auth_tocken = self.post(
                'user.login',
                {user_field: self._user, 'password': self._passwd})
        return self._auth_tocken

    def _get_id(self):
        self._id += 1
        return self._id

    def _get_json(self, method, params):
        if method == 'user.login' or method == 'apiinfo.version':
            data = OrderedDict([
                ('jsonrpc', '2.0'),
                ('method', method),
                ('params', params),
                ('id', self._get_id())
            ])
        else:
            data = OrderedDict([
                ('jsonrpc', '2.0'),
                ('method', method),
                ('params', params),
                ('auth', self._auth()),
                ('id', self._get_id())
            ])
        return json.dumps(data, sort_keys=False)

    def post(self, method, params):
        request = urllib2.Request(self._url)
        request.add_header('Content-Type', 'application/json; charset=utf-8')
        data = self._get_json(method, params)
        logging.debug('Post to zabbix: {0}'.format(data))
        data = bytearray(data, 'utf-8')
        response = urllib2.urlopen(request, data)
        logging.debug('Zabbix response code: {0}'.format(response.code))
        if response.code == 200:
            body = response.read()
            body = body.decode('utf-8')
            logging.debug('Zabbix response body: {0}'.format(body))
        else:
            raise Exception('Response code: {0}'.format(response.code))
        data = json.loads(body)
        if 'error' in data:
            raise Exception('Error response from zabbix api: {0}'.format(
                json.dumps(data['error'], indent=2)))
        return data['result']
