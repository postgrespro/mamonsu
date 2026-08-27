# -*- coding: utf-8 -*-

"""Unit tests for the TLS settings of the Zabbix sender.

They need neither docker nor a Zabbix server. Run from the repository root:

    python -m pytest tests/unit
"""

import logging
import socket

import pytest

from mamonsu.lib.senders import tls
from mamonsu.lib.senders.zbx import ZbxSender, TLS_CERT, TLS_PSK, TLS_UNENCRYPTED

PSK_HEX = 'd1e4b7a9c2f30516a8b7c6d5e4f30219a8b7c6d5e4f302198a7b6c5d4e3f2011'
PSK_BYTES = bytes(bytearray.fromhex(PSK_HEX))


class FakeConfig(object):
    """Just enough of Config for ZbxSender._setup_tls()."""

    def __init__(self, **options):
        self.options = options

    def fetch(self, section, key, klass=None, raw=False):
        assert section == 'zabbix'
        value = self.options.get(key)
        if not raw and isinstance(value, str) and '%' in value:
            # mimic configparser: a bare '%' in an interpolated read raises
            raise ValueError('interpolation syntax error in {0}'.format(key))
        return value


def make_sender(**options):
    sender = ZbxSender.__new__(ZbxSender)
    sender.log = logging.getLogger('test-zbx-sender')
    sender._enabled = True
    sender.host, sender.port, sender.timeout = 'zabbix', 10051, 15
    sender._setup_tls(FakeConfig(**options))
    return sender


#  PSK file parsing


def test_read_psk_file(tmp_path):
    path = tmp_path / 'zabbix_agentd.psk'
    path.write_text(PSK_HEX + '\n')
    assert tls.read_psk_file(str(path)) == PSK_BYTES


def test_read_psk_file_ignores_whitespace(tmp_path):
    path = tmp_path / 'zabbix_agentd.psk'
    path.write_text('  ' + PSK_HEX[:32] + '\n' + PSK_HEX[32:] + '  \n\n')
    assert tls.read_psk_file(str(path)) == PSK_BYTES


def test_read_psk_file_missing(tmp_path):
    with pytest.raises(tls.TLSError) as error:
        tls.read_psk_file(str(tmp_path / 'nope.psk'))
    assert 'can\'t read PSK file' in str(error.value)


def test_read_psk_file_too_short(tmp_path):
    path = tmp_path / 'short.psk'
    path.write_text('abcdef\n')
    with pytest.raises(tls.TLSError) as error:
        tls.read_psk_file(str(path))
    assert 'hex digits' in str(error.value)


def test_read_psk_file_odd_length(tmp_path):
    path = tmp_path / 'odd.psk'
    path.write_text(PSK_HEX + 'a')
    with pytest.raises(tls.TLSError) as error:
        tls.read_psk_file(str(path))
    assert 'odd number' in str(error.value)


def test_read_psk_file_not_hex(tmp_path):
    path = tmp_path / 'garbage.psk'
    secret = 'zzzz' + PSK_HEX[4:]
    path.write_text(secret)
    with pytest.raises(tls.TLSError) as error:
        tls.read_psk_file(str(path))
    # the file content must never end up in a message that goes to the log
    assert secret not in str(error.value)
    assert 'not a valid hex string' in str(error.value)


#  configuration of the sender


def test_no_tls_options_keeps_previous_behaviour():
    sender = make_sender()
    assert sender.tls_connect == TLS_UNENCRYPTED
    assert sender._enabled is True
    assert sender._psk is None


def test_psk_options_are_loaded(tmp_path):
    path = tmp_path / 'zabbix_agentd.psk'
    path.write_text(PSK_HEX)
    sender = make_sender(
        tls_connect='psk', tls_psk_identity='PSK 001', tls_psk_file=str(path))
    assert sender.tls_connect == TLS_PSK
    assert sender._enabled is True
    assert sender._psk == PSK_BYTES


def test_psk_value_is_case_insensitive(tmp_path):
    path = tmp_path / 'zabbix_agentd.psk'
    path.write_text(PSK_HEX)
    sender = make_sender(
        tls_connect='PSK', tls_psk_identity='PSK 001', tls_psk_file=str(path))
    assert sender.tls_connect == TLS_PSK


def test_unknown_tls_connect_disables_sender():
    sender = make_sender(tls_connect='ssl')
    assert sender._enabled is False


def test_psk_without_identity_disables_sender(tmp_path):
    path = tmp_path / 'zabbix_agentd.psk'
    path.write_text(PSK_HEX)
    sender = make_sender(tls_connect='psk', tls_psk_file=str(path))
    assert sender._enabled is False


def test_psk_without_file_disables_sender():
    sender = make_sender(tls_connect='psk', tls_psk_identity='PSK 001')
    assert sender._enabled is False


def test_unreadable_psk_file_disables_sender(tmp_path):
    sender = make_sender(
        tls_connect='psk', tls_psk_identity='PSK 001',
        tls_psk_file=str(tmp_path / 'nope.psk'))
    assert sender._enabled is False


#  transport selection


def test_connect_without_tls_uses_plain_socket(monkeypatch):
    calls = {}

    class FakeSocket(object):
        def settimeout(self, timeout):
            calls['timeout'] = timeout

        def connect(self, address):
            calls['address'] = address

    monkeypatch.setattr(socket, 'socket', lambda *a, **kw: FakeSocket())
    monkeypatch.setattr(
        tls, 'connect_psk',
        lambda *a, **kw: pytest.fail('TLS must not be used without tls_connect = psk'))
    sender = make_sender()
    assert isinstance(sender._connect(), FakeSocket)
    assert calls == {'timeout': 15, 'address': ('zabbix', 10051)}


def test_connect_with_psk_uses_tls(monkeypatch, tmp_path):
    path = tmp_path / 'zabbix_agentd.psk'
    path.write_text(PSK_HEX)
    calls = {}
    marker = object()

    def fake_connect_psk(host, port, identity, psk, timeout, ciphers=None):
        calls.update(
            host=host, port=port, identity=identity, psk=psk,
            timeout=timeout, ciphers=ciphers)
        return marker

    monkeypatch.setattr(tls, 'connect_psk', fake_connect_psk)
    monkeypatch.setattr(
        socket, 'socket',
        lambda *a, **kw: pytest.fail('plain socket must not be used with tls_connect = psk'))
    sender = make_sender(
        tls_connect='psk', tls_psk_identity='PSK 001', tls_psk_file=str(path))
    assert sender._connect() is marker
    assert calls == {
        'host': 'zabbix', 'port': 10051, 'identity': 'PSK 001',
        'psk': PSK_BYTES, 'timeout': 15, 'ciphers': None}


def test_connect_psk_rejects_empty_identity():
    with pytest.raises(tls.TLSError) as error:
        tls.connect_psk('zabbix', 10051, '', PSK_BYTES, 15)
    assert 'tls_psk_identity' in str(error.value)


#  certificates


def test_cert_options_are_loaded():
    sender = make_sender(
        tls_connect='cert', tls_ca_file='/etc/zabbix/ca.crt',
        tls_cert_file='/etc/zabbix/mamonsu.crt', tls_key_file='/etc/zabbix/mamonsu.key',
        tls_server_cert_issuer='CN=CA,O=Company')
    assert sender.tls_connect == TLS_CERT
    assert sender._enabled is True
    assert sender.tls_server_cert_issuer == 'CN=CA,O=Company'


def test_cert_without_key_disables_sender():
    sender = make_sender(
        tls_connect='cert', tls_ca_file='/etc/zabbix/ca.crt',
        tls_cert_file='/etc/zabbix/mamonsu.crt')
    assert sender._enabled is False


def test_connect_with_cert_uses_tls(monkeypatch):
    calls = {}
    marker = object()

    def fake_connect_cert(host, port, ca_file, cert_file, key_file, timeout, **kwargs):
        calls.update(
            host=host, port=port, ca_file=ca_file, cert_file=cert_file,
            key_file=key_file, timeout=timeout, **kwargs)
        return marker

    monkeypatch.setattr(tls, 'connect_cert', fake_connect_cert)
    monkeypatch.setattr(
        socket, 'socket',
        lambda *a, **kw: pytest.fail('plain socket must not be used with tls_connect = cert'))
    sender = make_sender(
        tls_connect='cert', tls_ca_file='ca.crt', tls_cert_file='m.crt',
        tls_key_file='m.key', tls_crl_file='ca.crl',
        tls_server_cert_subject='CN=zabbix,O=Company')
    assert sender._connect() is marker
    assert calls == {
        'host': 'zabbix', 'port': 10051, 'ca_file': 'ca.crt', 'cert_file': 'm.crt',
        'key_file': 'm.key', 'timeout': 15, 'crl_file': 'ca.crl', 'ciphers': None,
        'server_cert_issuer': None, 'server_cert_subject': 'CN=zabbix,O=Company'}


def test_connect_cert_requires_files():
    with pytest.raises(tls.TLSError) as error:
        tls.connect_cert('zabbix', 10051, None, 'm.crt', 'm.key', 15)
    assert 'tls_ca_file' in str(error.value)


#  distinguished names


def test_parse_dn():
    assert tls.parse_dn('CN=zabbix server,O=Company') == [
        ('commonName', 'zabbix server'), ('organizationName', 'Company')]


def test_parse_dn_keeps_escaped_commas():
    assert tls.parse_dn(r'CN=Company\, Inc,OU=IT') == [
        ('commonName', 'Company, Inc'), ('organizationalUnitName', 'IT')]


def test_parse_dn_accepts_long_names():
    assert tls.parse_dn('commonName=zabbix') == [('commonName', 'zabbix')]


def test_check_dn_ignores_attribute_order():
    peer = ((('organizationName', 'Company'),), (('commonName', 'zabbix'),))
    tls.check_dn(peer, 'CN=zabbix,O=Company', 'subject')


def test_check_dn_reports_a_mismatch():
    peer = ((('commonName', 'zabbix'),),)
    with pytest.raises(tls.TLSError) as error:
        tls.check_dn(peer, 'CN=other', 'issuer')
    assert 'does not match tls_server_cert_issuer' in str(error.value)


def test_check_dn_without_expectation_accepts_anything():
    tls.check_dn(None, None, 'subject')


#  command line


def test_command_line_overrides_config():
    from mamonsu.lib.runner import apply_zabbix_tls_args

    class FakeArgs(object):
        zabbix_tls_connect = 'psk'
        zabbix_tls_psk_identity = 'PSK 001'
        zabbix_tls_psk_file = '/etc/zabbix/zabbix_agentd.psk'
        zabbix_tls_ca_file = None
        zabbix_tls_crl_file = None
        zabbix_tls_cert_file = None
        zabbix_tls_key_file = None
        zabbix_tls_server_cert_issuer = None
        zabbix_tls_server_cert_subject = None

    class FakeCfg(object):
        def __init__(self):
            self.values = {}
            self.config = self

        def set(self, section, key, value):
            self.values[(section, key)] = value

    cfg = FakeCfg()
    apply_zabbix_tls_args(cfg, FakeArgs())
    # options that were not given on the command line keep the config file value
    assert cfg.values == {
        ('zabbix', 'tls_connect'): 'psk',
        ('zabbix', 'tls_psk_identity'): 'PSK 001',
        ('zabbix', 'tls_psk_file'): '/etc/zabbix/zabbix_agentd.psk'}


#  review fixes


def test_percent_in_tls_values_is_read_literally(tmp_path):
    """tls_* settings are free text and must be fetched without interpolation."""
    path = tmp_path / 'zabbix_agentd.psk'
    path.write_text(PSK_HEX)
    sender = make_sender(
        tls_connect='psk', tls_psk_identity='PSK%01', tls_psk_file=str(path))
    assert sender._enabled is True
    assert sender.tls_psk_identity == 'PSK%01'


def test_connect_refuses_unknown_tls_mode(monkeypatch):
    """Even a caller that ignores _enabled (mamonsu upload) gets no plaintext."""
    monkeypatch.setattr(
        socket, 'socket',
        lambda *a, **kw: pytest.fail(
            'an unknown tls_connect must not fall back to a plain socket'))
    sender = make_sender(tls_connect='ssl')
    assert sender._enabled is False
    with pytest.raises(tls.TLSError) as error:
        sender._connect()
    assert 'refusing to send data unencrypted' in str(error.value)


def test_libssl_transport_is_refused_on_macos(monkeypatch):
    """The macOS libssl stub aborts the process, so it must never be loaded."""
    import sys as _sys
    monkeypatch.setattr(tls, '_libssl', None)
    monkeypatch.setattr(tls, '_libcrypto', None)
    monkeypatch.setattr(_sys, 'platform', 'darwin')
    with pytest.raises(tls.TLSError) as error:
        tls._libs()
    assert 'Python 3.13' in str(error.value)
