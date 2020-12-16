# -*- coding: utf-8 -*-

# https://www.zabbix.com/documentation/2.0/ru/manual/appendix/items/activepassive

import time
import struct
import socket
import json
import logging

from mamonsu.lib.plugin import Plugin
from mamonsu.lib.queue import Queue
from itertools import islice


class ZbxSender(Plugin):
    Interval = 10
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
        self.re_send = config.fetch('zabbix', 're_send', bool)
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
        clock = int(time.time())
        data = json.dumps({
            'request': 'sender data',
            'data': metrics,
            'clock': clock
        })
        sent_all = self._send_data(data)
        if not sent_all and self.re_send:
            for metric in metrics:
                data = json.dumps({
                    'request': 'sender data',
                    'data': [metric],
                    'clock': clock
                })
                self._send_data(data)
                
    def send_file_to_zabbix(self, path):
        zabbix_client = self.config.fetch('zabbix', 'client')
        self.log.setLevel((self.config.fetch('log', 'level')).upper())

        metrics = []
        with open(path, 'r') as f:
            while True:
                lines = list(islice(f, 100))
                for line in lines:
                    try:
                        split_line = line.rstrip('\n').split('\t')
                        if len(split_line) == 3:
                            metric = {
                                'host': zabbix_client,
                                'key': split_line[2],
                                'value': split_line[1],
                                'clock': int(split_line[0])}
                            metrics.append(metric)
                        else:
                            self.log.error(
                                'Can\'t load metric in line: "{0}". The line must have the format: '
                                'time <tab> value <tab> metric\'s name.'.format(
                                    line.rstrip('\n')))
                    except Exception as e:
                        self.log.error('Can\'t load metric in line: "{0}". Error : {1} '.format(line.rstrip('\n'), e, ))

                data = json.dumps({
                    'request': 'sender data',
                    'data': metrics,
                    'clock': int(time.time())
                })
                self._send_data(data)
                self.log.info('sended {0} metrics'.format(str(len(metrics))))
                metrics = []
                if not lines:
                    break

    def _send_data(self, data):
        sent_all = True
        data_len = struct.pack('<Q', len(data))
        packet = b'ZBXD\x01' + data_len + str.encode(data)
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
                sent_all = False
                self.log.error(
                    'On request:\n{0}\nget response'
                    ' with failed items:\n{1}'.format(
                        data,
                        resp_body))
        finally:
            sock.close()
        return sent_all

    def _receive(self, sock, count):
        buf = str.encode('')
        while len(buf) < count:
            chunk = sock.recv(count - len(buf))
            if not chunk:
                break
            buf += chunk
        return buf
