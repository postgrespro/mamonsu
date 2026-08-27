# -*- coding: utf-8 -*-

"""The unencrypted sender must behave exactly as it did before TLS was added.

A fake Zabbix trapper is started on the loopback interface, so these tests need
neither a Zabbix server nor docker:

    python -m pytest tests/unit/test_zbx_sender_socket.py
    python3 tests/unit/test_zbx_sender_socket.py
"""

import json
import logging
import os
import socket
import struct
import sys
import threading

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from mamonsu.lib.senders.zbx import ZbxSender  # noqa: E402

HEADER = b'ZBXD' + b'\x01'
SUCCESS = '{"response":"success","info":"processed: 1; failed: 0; total: 1; seconds spent: 0.1"}'
PARTIAL = '{"response":"success","info":"processed: 1; failed: 1; total: 2; seconds spent: 0.1"}'


class FakeConfig(object):
    def fetch(self, section, key, klass=None, raw=False):
        return None


class FakeTrapper(object):
    """Accepts one connection, replies in the Zabbix sender protocol."""

    def __init__(self, response):
        self.response = response
        self.request = None
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('127.0.0.1', 0))
        self.socket.listen(1)
        self.port = self.socket.getsockname()[1]
        self.thread = threading.Thread(target=self._serve)
        self.thread.daemon = True
        self.thread.start()

    def _receive(self, conn, count):
        buf = b''
        while len(buf) < count:
            chunk = conn.recv(count - len(buf))
            if not chunk:
                break
            buf += chunk
        return buf

    def _serve(self):
        conn, _ = self.socket.accept()
        try:
            header = self._receive(conn, 13)
            body = self._receive(conn, struct.unpack('<Q', header[5:])[0])
            self.request = (header, body)
            payload = self.response.encode('utf-8')
            conn.sendall(HEADER + struct.pack('<Q', len(payload)) + payload)
        finally:
            conn.close()

    def close(self):
        self.thread.join(10)
        self.socket.close()


def make_sender(port):
    sender = ZbxSender.__new__(ZbxSender)
    sender.log = logging.getLogger('test-zbx-sender')
    sender._enabled = True
    sender.host, sender.port, sender.timeout = '127.0.0.1', port, 5
    sender._setup_tls(FakeConfig())
    return sender


def metrics_packet():
    return json.dumps({
        'request': 'sender data',
        'data': [{'host': 'db2', 'key': 'pgsql.ping[]', 'value': '1', 'clock': 1700000000}],
        'clock': 1700000000})


def test_send_data_over_plain_socket():
    trapper = FakeTrapper(SUCCESS)
    try:
        data = metrics_packet()
        assert make_sender(trapper.port)._send_data(data) is True
    finally:
        trapper.close()
    header, body = trapper.request
    # the wire format has to stay byte for byte what Zabbix expects
    assert header[:5] == HEADER
    assert struct.unpack('<Q', header[5:])[0] == len(data)
    assert json.loads(body.decode('utf-8')) == json.loads(data)


def test_failed_items_are_reported():
    trapper = FakeTrapper(PARTIAL)
    try:
        assert make_sender(trapper.port)._send_data(metrics_packet()) is False
    finally:
        trapper.close()


def main():
    for test in (test_send_data_over_plain_socket, test_failed_items_are_reported):
        test()
        print('ok: {0}'.format(test.__name__))
    return 0


if __name__ == '__main__':
    sys.exit(main())
