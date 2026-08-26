# -*- coding: utf-8 -*-

# https://www.zabbix.com/documentation/2.0/ru/manual/appendix/items/activepassive

import time
import struct
import socket
import json
import logging

from mamonsu.lib.plugin import Plugin
from mamonsu.lib.queue import Queue
from mamonsu.lib.senders import tls
from itertools import islice


TLS_UNENCRYPTED = 'unencrypted'
TLS_PSK = 'psk'
TLS_CERT = 'cert'


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
        self.timeout = config.fetch('zabbix', 'timeout')
        self.re_send = config.fetch('zabbix', 're_send', bool)
        self.queue = Queue()
        self.log = logging.getLogger(
            'ZBX-{0}:{1}'.format(self.host, self.port))
        self._setup_tls(config)

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

    def _setup_tls(self, config):
        """Read TLS settings. Without them the sender behaves exactly as before."""
        # raw=True: identities, distinguished names and paths are free text,
        # a '%' in them must not trigger configparser interpolation
        self.tls_connect = (config.fetch('zabbix', 'tls_connect', raw=True) or TLS_UNENCRYPTED).lower()
        self.tls_psk_identity = config.fetch('zabbix', 'tls_psk_identity', raw=True)
        self.tls_psk_file = config.fetch('zabbix', 'tls_psk_file', raw=True)
        self.tls_cipher_psk = config.fetch('zabbix', 'tls_cipher_psk', raw=True)
        self.tls_cipher_cert = config.fetch('zabbix', 'tls_cipher_cert', raw=True)
        self.tls_ca_file = config.fetch('zabbix', 'tls_ca_file', raw=True)
        self.tls_crl_file = config.fetch('zabbix', 'tls_crl_file', raw=True)
        self.tls_cert_file = config.fetch('zabbix', 'tls_cert_file', raw=True)
        self.tls_key_file = config.fetch('zabbix', 'tls_key_file', raw=True)
        self.tls_server_cert_issuer = config.fetch('zabbix', 'tls_server_cert_issuer', raw=True)
        self.tls_server_cert_subject = config.fetch('zabbix', 'tls_server_cert_subject', raw=True)
        self._psk = None
        if self.tls_connect == TLS_UNENCRYPTED:
            return
        # a misconfigured encrypted sender must never quietly fall back to
        # plaintext, so the plugin is disabled instead
        if self.tls_connect not in (TLS_PSK, TLS_CERT):
            self._disable(
                'unknown tls_connect value "{0}", expected one of: {1}'.format(
                    self.tls_connect, ', '.join([TLS_UNENCRYPTED, TLS_PSK, TLS_CERT])))
            return
        if self.tls_connect == TLS_CERT:
            missing = [name for name, value in (
                ('tls_ca_file', self.tls_ca_file),
                ('tls_cert_file', self.tls_cert_file),
                ('tls_key_file', self.tls_key_file)) if not value]
            if missing:
                self._disable(
                    'tls_connect = cert requires {0}'.format(', '.join(missing)))
                return
            self.log.info('sending metrics over TLS with a certificate')
            return
        if not self.tls_psk_identity or not self.tls_psk_file:
            self._disable(
                'tls_connect = psk requires both tls_psk_identity and tls_psk_file')
            return
        try:
            self._psk = tls.read_psk_file(self.tls_psk_file)
        except tls.TLSError as e:
            self._disable('{0}'.format(e))
            return
        self.log.info(
            'sending metrics over TLS-PSK, identity: {0}'.format(self.tls_psk_identity))

    def _disable(self, reason):
        self._enabled = False
        self.log.error(reason)

    def _connect(self):
        if self.tls_connect == TLS_PSK:
            return tls.connect_psk(
                self.host, self.port, self.tls_psk_identity, self._psk,
                int(self.timeout), self.tls_cipher_psk)
        if self.tls_connect == TLS_CERT:
            return tls.connect_cert(
                self.host, self.port, self.tls_ca_file, self.tls_cert_file,
                self.tls_key_file, int(self.timeout),
                crl_file=self.tls_crl_file, ciphers=self.tls_cipher_cert,
                server_cert_issuer=self.tls_server_cert_issuer,
                server_cert_subject=self.tls_server_cert_subject)
        if self.tls_connect != TLS_UNENCRYPTED:
            # _setup_tls() disables the plugin, but send_file_to_zabbix() does
            # not honour that flag - a misconfigured sender must fail here too
            # rather than fall through to an unencrypted connection
            raise tls.TLSError(
                'unknown tls_connect value "{0}", refusing to send data'
                ' unencrypted'.format(self.tls_connect))
        sock = socket.socket()
        try:
            sock.settimeout(int(self.timeout))
            sock.connect((self.host, self.port))
        except Exception:
            # a failed connect() would otherwise leak the file descriptor
            # until the socket is garbage collected
            sock.close()
            raise
        return sock

    def _send_data(self, data):
        sent_all = True
        data_len = struct.pack('<Q', len(data))
        packet = b'ZBXD\x01' + data_len + str.encode(data)
        sock = self._connect()
        try:
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
