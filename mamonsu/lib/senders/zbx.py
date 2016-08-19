# -*- coding: utf-8 -*-

# https://www.zabbix.com/documentation/2.0/ru/manual/appendix/items/activepassive

import time
import struct
import socket
import json
import logging
import encodings.idna

import mamonsu.lib.platform as platform
from mamonsu.lib.plugin import Plugin
from mamonsu.lib.queue import Queue


class ZbxSender(Plugin):

    Interval = 2
    _sender = True

    def __init__(self, config):
        super(ZbxSender, self).__init__(config)
        self.host = config.fetch('zabbix', 'address')
        if self.host is None:
            self._enabled = False
        elif not config.fetch('zabbix', 'enabled', bool):
            self._enabled = False
        self.port = config.fetch('zabbix', 'port', int)
        self.max_queue_size = config.fetch('sender', 'queue', int)
        self.fqdn = config.fetch('zabbix', 'client')
        self.queue = Queue()
        self.log = logging.getLogger(
            'ZBX-{0}:{1}'.format(self.host, self.port))

    def send(self, key, value, host=None, clock=None):
        if host is None:
            host = self.fqdn
        if clock is None:
            clock = int(time.time())
        metric = {
            'host': host, 'key': key,
            'value': str(value), 'clock': clock}
        self._send(metric)

    def _send(self, metric):
        if self.queue.size() > self.max_queue_size:
            self.log.error('Queue size over limit, replace last metric')
            self.queue.replace(metric)
        else:
            self.queue.add(metric)

    def run(self, zbx):
        self._flush()

    def _flush(self):
        metrics = self.queue.flush()
        if len(metrics) == 0:
            return
        data = json.dumps({
            'request': 'sender data',
            'data': metrics,
            'clock': int(time.time())
        })
        self._send_data(data)

    def _send_data(self, data):
        data_len = struct.pack('<Q', len(data))
        if platform.PY3:
            packet = b'ZBXD\x01' + data_len + str.encode(data)
        else:
            packet = 'ZBXD\x01' + data_len + data
        try:
            sock = socket.socket()
            sock.connect((self.host, self.port))
            self.log.debug('request: {0}'.format(data))
            sock.sendall(packet)
            resp_header = self._receive(sock, 13)
            resp_body_len = struct.unpack('<Q', resp_header[5:])[0]
            resp_body = self._receive(sock, resp_body_len)
            self.log.debug('response: {0}'.format(resp_body))
            if 'failed: 0' not in str(resp_body):
                self.log.error(
                    'On request:\n{0}\nget response'
                    ' with failed items:\n{1}'.format(
                        data,
                        resp_body))
        finally:
            sock.close()

    def _receive(self, sock, count):
        buf = str.encode('')
        while len(buf) < count:
            chunk = sock.recv(count - len(buf))
            if not chunk:
                break
            buf += chunk
        return buf
