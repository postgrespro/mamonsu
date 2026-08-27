# -*- coding: utf-8 -*-

"""TLS handshakes against a real TLS server ("openssl s_server").

These are the only tests that exercise the transports end to end, so they are
worth running on every platform mamonsu is packaged for. They need the openssl
binary and a loopback socket, no Zabbix server and no docker.

    python -m pytest tests/unit/test_tls_openssl.py     # with pytest
    python3 tests/unit/test_tls_openssl.py              # without it
"""

import os
import socket
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from mamonsu.lib.senders import tls  # noqa: E402

try:
    import pytest
except ImportError:  # the file is also runnable as a plain script
    pytest = None

PSK_HEX = 'd1e4b7a9c2f30516a8b7c6d5e4f30219a8b7c6d5e4f302198a7b6c5d4e3f2011'
PSK_BYTES = bytes(bytearray.fromhex(PSK_HEX))
WRONG_PSK = bytes(bytearray.fromhex('00' * 32))
IDENTITY = 'PSK 001'

CA_DN = 'CN=Mamonsu Test CA,O=Mamonsu'
SERVER_DN = 'CN=zabbix server,O=Mamonsu'
CLIENT_DN = 'CN=mamonsu,O=Mamonsu'


def no_openssl_binary():
    try:
        subprocess.check_output(['openssl', 'version'], stderr=subprocess.STDOUT)
    except (OSError, subprocess.CalledProcessError):
        return 'the openssl binary is not available'
    return None


def no_libssl():
    if sys.platform == 'win32':
        return 'the libssl transport is not used on Windows'
    return no_openssl_binary()


def skip_unless(reason_func):
    """Skip under pytest, and let main() report the same reason without it."""
    def decorator(function):
        function.skip_reason = reason_func
        if pytest is None:
            return function
        reason = reason_func()
        return pytest.mark.skipif(reason is not None, reason=reason or '')(function)
    return decorator


def free_port():
    sock = socket.socket()
    try:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]
    finally:
        sock.close()


def start_server(port, options):
    """Start an s_server that echoes back reversed text."""
    process = subprocess.Popen(
        ['openssl', 's_server', '-accept', str(port), '-tls1_2', '-rev', '-quiet'] + options,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.time() + 10
    while time.time() < deadline:
        probe = socket.socket()
        try:
            probe.settimeout(0.5)
            probe.connect(('127.0.0.1', port))
            return process
        except socket.error:
            time.sleep(0.1)
        finally:
            probe.close()
    process.kill()
    raise AssertionError('openssl s_server did not start')


def stop_server(process):
    if process.poll() is None:
        process.kill()
    process.wait()


def openssl(*args):
    subprocess.check_output(['openssl'] + list(args), stderr=subprocess.STDOUT)


def make_certificates(directory):
    """Issue a CA, a server and a client certificate, as Zabbix would need."""
    path = lambda name: os.path.join(str(directory), name)  # noqa: E731

    def subject(dn):
        # openssl wants /CN=x/O=y, the config file format is CN=x,O=y
        return '/' + '/'.join(reversed(dn.split(',')))

    openssl('req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '1',
            '-keyout', path('ca.key'), '-out', path('ca.crt'), '-subj', subject(CA_DN))
    for name, dn in (('server', SERVER_DN), ('client', CLIENT_DN)):
        openssl('req', '-newkey', 'rsa:2048', '-nodes',
                '-keyout', path(name + '.key'), '-out', path(name + '.csr'),
                '-subj', subject(dn))
        openssl('x509', '-req', '-in', path(name + '.csr'), '-days', '1',
                '-CA', path('ca.crt'), '-CAkey', path('ca.key'), '-CAcreateserial',
                '-out', path(name + '.crt'))
    return path


#  PSK


@skip_unless(no_libssl)
def test_psk_handshake_and_data():
    """The connection is established and carries data in both directions."""
    port = free_port()
    process = start_server(port, ['-nocert', '-psk_identity', IDENTITY, '-psk', PSK_HEX])
    try:
        sock = tls.connect_psk('127.0.0.1', port, IDENTITY, PSK_BYTES, 10)
        try:
            assert sock.version() == 'TLSv1.2'
            sock.sendall(b'ping\n')
            assert sock.recv(64).strip() == b'gnip'
        finally:
            sock.close()
    finally:
        stop_server(process)


@skip_unless(no_libssl)
def test_wrong_psk_is_reported():
    """A key mismatch fails the handshake instead of sending anything."""
    port = free_port()
    process = start_server(port, ['-nocert', '-psk_identity', IDENTITY, '-psk', PSK_HEX])
    try:
        try:
            tls.connect_psk('127.0.0.1', port, IDENTITY, WRONG_PSK, 10)
        except tls.TLSError as error:
            assert 'handshake failed' in str(error)
        else:
            raise AssertionError('a wrong PSK must not produce a connection')
    finally:
        stop_server(process)


#  certificates


def cert_server(port, path):
    return start_server(port, [
        '-cert', path('server.crt'), '-key', path('server.key'),
        '-CAfile', path('ca.crt'), '-Verify', '1'])


@skip_unless(no_openssl_binary)
def test_cert_handshake_and_data(tmp_path):
    path = make_certificates(tmp_path)
    port = free_port()
    process = cert_server(port, path)
    try:
        sock = tls.connect_cert(
            '127.0.0.1', port, path('ca.crt'), path('client.crt'), path('client.key'), 10,
            server_cert_issuer=CA_DN, server_cert_subject=SERVER_DN)
        try:
            sock.sendall(b'ping\n')
            assert sock.recv(64).strip() == b'gnip'
        finally:
            sock.close()
    finally:
        stop_server(process)


@skip_unless(no_openssl_binary)
def test_cert_subject_mismatch_is_reported(tmp_path):
    path = make_certificates(tmp_path)
    port = free_port()
    process = cert_server(port, path)
    try:
        try:
            tls.connect_cert(
                '127.0.0.1', port, path('ca.crt'), path('client.crt'), path('client.key'), 10,
                server_cert_subject='CN=someone else,O=Mamonsu')
        except tls.TLSError as error:
            assert 'does not match tls_server_cert_subject' in str(error)
        else:
            raise AssertionError('a foreign server certificate must be rejected')
    finally:
        stop_server(process)


@skip_unless(no_openssl_binary)
def test_unknown_ca_is_rejected(tmp_path):
    path = make_certificates(tmp_path)
    other = tmp_path / 'other'
    other.mkdir()
    other_path = make_certificates(other)
    port = free_port()
    process = cert_server(port, path)
    try:
        try:
            tls.connect_cert(
                '127.0.0.1', port, other_path('ca.crt'),
                path('client.crt'), path('client.key'), 10)
        except tls.TLSError as error:
            assert 'handshake failed' in str(error)
        else:
            raise AssertionError('a server signed by an unknown CA must be rejected')
    finally:
        stop_server(process)


def main():
    import tempfile
    import shutil
    from pathlib import Path

    failures = 0
    for test in (test_psk_handshake_and_data, test_wrong_psk_is_reported,
                 test_cert_handshake_and_data, test_cert_subject_mismatch_is_reported,
                 test_unknown_ca_is_rejected):
        reason = test.skip_reason()
        if reason:
            print('skipped: {0} ({1})'.format(test.__name__, reason))
            continue
        if test.__code__.co_argcount:
            directory = Path(tempfile.mkdtemp())
            try:
                test(directory)
            finally:
                shutil.rmtree(directory, ignore_errors=True)
        else:
            test()
        print('ok: {0}'.format(test.__name__))
    return failures


if __name__ == '__main__':
    sys.exit(main())
