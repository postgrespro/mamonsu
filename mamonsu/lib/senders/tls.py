# -*- coding: utf-8 -*-

# TLS-PSK transport for the Zabbix sender.
#
# ssl.SSLContext.set_psk_client_callback() appeared in Python 3.13, while the
# distributions mamonsu is packaged for still ship 3.7 (Astra Linux 1.7) or
# 3.11 (Astra Linux 1.8). For those the handshake is done through libssl
# directly: only the public OpenSSL API is used, no CPython internals, so the
# same code works with libssl.so.1.1 (OpenSSL 1.1.1) and libssl.so.3
# (OpenSSL 3.x).

import ctypes
import ctypes.util
import os
import socket
import ssl
import struct
import sys

# TLS 1.3 negotiates PSK through a different callback (psk_use_session), so the
# PSK connection is pinned to TLS 1.2, which every Zabbix server built with
# OpenSSL supports.
TLS1_2_VERSION = 0x0303

# ssl/ssl.h
SSL_CTRL_SET_MIN_PROTO_VERSION = 123
SSL_CTRL_SET_MAX_PROTO_VERSION = 124

SSL_ERROR_NONE = 0
SSL_ERROR_SSL = 1
SSL_ERROR_WANT_READ = 2
SSL_ERROR_WANT_WRITE = 3
SSL_ERROR_SYSCALL = 5
SSL_ERROR_ZERO_RETURN = 6

# minimal length Zabbix accepts for a PSK: 128 bits, i.e. 32 hex digits
MIN_PSK_HEX_LEN = 32

DEFAULT_PSK_CIPHERS = 'PSK'

# short names of the DN attributes Zabbix uses in TLSServerCertIssuer /
# TLSServerCertSubject, mapped to the long names OpenSSL reports
DN_ATTRIBUTES = {
    'CN': 'commonName',
    'O': 'organizationName',
    'OU': 'organizationalUnitName',
    'C': 'countryName',
    'ST': 'stateOrProvinceName',
    'L': 'localityName',
    'DC': 'domainComponent',
    'STREET': 'streetAddress',
    'UID': 'userId',
}

# OpenSSL 1.0.x is not listed: it has neither TLS_client_method() nor
# SSL_CTRL_SET_MIN/MAX_PROTO_VERSION, so it can't be used here anyway
LIBSSL_NAMES = ['libssl.so.3', 'libssl.so.1.1', 'libssl.so']
LIBCRYPTO_NAMES = ['libcrypto.so.3', 'libcrypto.so.1.1', 'libcrypto.so']


class TLSError(Exception):
    pass


def stdlib_psk_supported():
    return hasattr(ssl.SSLContext, 'set_psk_client_callback')


def read_psk_file(path):
    """Read a Zabbix PSK file (a single line of hex digits) and return raw bytes.

    The value itself is never logged or included in exception messages.
    """
    try:
        with open(path, 'r') as fd:
            content = fd.read()
    except (IOError, OSError) as e:
        raise TLSError('can\'t read PSK file {0}: {1}'.format(path, e.strerror or e))
    psk_hex = ''.join(content.split())
    if len(psk_hex) < MIN_PSK_HEX_LEN:
        raise TLSError(
            'PSK file {0} contains less than {1} hex digits'.format(path, MIN_PSK_HEX_LEN))
    if len(psk_hex) % 2 != 0:
        raise TLSError('PSK file {0} contains an odd number of hex digits'.format(path))
    try:
        psk = bytes(bytearray.fromhex(psk_hex))
    except (ValueError, TypeError):
        raise TLSError('PSK file {0} is not a valid hex string'.format(path))
    return psk


def connect_psk(host, port, identity, psk, timeout, ciphers=None):
    """Open a TLS-PSK connection and return a socket-like object.

    The result implements sendall()/recv()/close(), which is all the Zabbix
    sender needs from a socket.
    """
    ciphers = ciphers or DEFAULT_PSK_CIPHERS
    if not identity:
        raise TLSError('tls_psk_identity is not set')
    if not psk:
        raise TLSError('PSK is empty')
    sock = socket.create_connection((host, port), timeout=timeout)
    try:
        if stdlib_psk_supported():
            return _wrap_stdlib(sock, identity, psk, ciphers)
        return OpenSSLSocket(sock, identity, psk, timeout, ciphers)
    except Exception:
        sock.close()
        raise


def _wrap_stdlib(sock, identity, psk, ciphers):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # a PSK handshake carries no certificates: both sides are authenticated by
    # the pre-shared key itself, and the connection fails if the keys differ
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_2
    try:
        context.set_ciphers(ciphers)
    except ssl.SSLError as e:
        raise TLSError('no PSK cipher suite available for "{0}": {1}'.format(ciphers, e))
    context.set_psk_client_callback(lambda hint: (identity, psk))
    try:
        return context.wrap_socket(sock)
    except ssl.SSLError as e:
        raise TLSError('TLS handshake failed: {0}'.format(e))


def connect_cert(host, port, ca_file, cert_file, key_file, timeout,
                 crl_file=None, ciphers=None,
                 server_cert_issuer=None, server_cert_subject=None):
    """Open a TLS connection authenticated by certificates.

    Like the Zabbix agent, the server is trusted through the CA file and,
    optionally, pinned by the issuer and subject of its certificate; the host
    name is deliberately not matched against the certificate, because Zabbix
    certificates are issued for the server, not for the address the agent uses.
    """
    for name, path in (('tls_ca_file', ca_file),
                       ('tls_cert_file', cert_file),
                       ('tls_key_file', key_file)):
        if not path:
            raise TLSError('{0} is not set'.format(name))
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_REQUIRED
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    try:
        context.load_verify_locations(cafile=ca_file)
        if crl_file:
            context.load_verify_locations(cafile=crl_file)
            context.verify_flags |= ssl.VERIFY_CRL_CHECK_LEAF
        context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    except (ssl.SSLError, IOError, OSError) as e:
        raise TLSError("can't load TLS certificates: {0}".format(e))
    if ciphers:
        try:
            context.set_ciphers(ciphers)
        except ssl.SSLError as e:
            raise TLSError('no cipher suite available for "{0}": {1}'.format(ciphers, e))
    sock = socket.create_connection((host, port), timeout=timeout)
    try:
        connection = context.wrap_socket(sock)
    except ssl.SSLError as e:
        sock.close()
        raise TLSError('TLS handshake failed: {0}'.format(e))
    except Exception:
        sock.close()
        raise
    try:
        peer = connection.getpeercert()
        check_dn(peer.get('issuer'), server_cert_issuer, 'issuer')
        check_dn(peer.get('subject'), server_cert_subject, 'subject')
    except Exception:
        connection.close()
        raise
    return connection


def parse_dn(dn):
    """Split "CN=zabbix,O=company" into pairs, honouring backslash escapes."""
    pairs, item, escaped = [], '', False
    for char in dn:
        if escaped:
            item += char
            escaped = False
        elif char == '\\':
            escaped = True
        elif char == ',':
            pairs.append(item)
            item = ''
        else:
            item += char
    pairs.append(item)
    result = []
    for pair in pairs:
        if not pair.strip():
            continue
        if '=' not in pair:
            raise TLSError("can't parse {0} as a distinguished name".format(dn))
        key, value = pair.split('=', 1)
        key = key.strip()
        result.append((DN_ATTRIBUTES.get(key.upper(), key), value.strip()))
    return result


def check_dn(peer_dn, expected, what):
    """Verify that every attribute of the configured DN is in the peer's one."""
    if not expected:
        return
    peer = set()
    for rdn in peer_dn or ():
        for key, value in rdn:
            peer.add((key, value))
    missing = [pair for pair in parse_dn(expected) if pair not in peer]
    if missing:
        raise TLSError(
            'certificate {0} does not match tls_server_cert_{0}: {1}'.format(
                what, ', '.join('{0}={1}'.format(*pair) for pair in missing)))


def _load_library(names, what):
    errors = []
    candidates = list(names)
    found = ctypes.util.find_library(what)
    if found is not None and found not in candidates:
        candidates.append(found)
    for name in candidates:
        try:
            return ctypes.CDLL(name, use_errno=True)
        except OSError as e:
            errors.append('{0}: {1}'.format(name, e))
    raise TLSError('can\'t load {0} ({1})'.format(what, '; '.join(errors)))


_libssl = None
_libcrypto = None


def _libs():
    """Load libssl/libcrypto once and declare the prototypes that are used."""
    global _libssl, _libcrypto
    if _libssl is not None:
        return _libssl, _libcrypto
    if sys.platform in ('win32', 'darwin'):
        # there is no loadable system libssl on these platforms (the macOS
        # /usr/lib/libssl.dylib stub aborts the process when loaded)
        raise TLSError('TLS-PSK requires Python 3.13 or newer on this platform')
    libssl = _load_library(LIBSSL_NAMES, 'ssl')
    libcrypto = _load_library(LIBCRYPTO_NAMES, 'crypto')

    # looking a symbol up raises AttributeError when the loaded library does not
    # export it, which is what happens on OpenSSL 1.0.x: report that plainly
    # instead of letting a bare AttributeError escape
    try:
        libssl.TLS_client_method.restype = ctypes.c_void_p
        libssl.SSL_CTX_new.argtypes = [ctypes.c_void_p]
        libssl.SSL_CTX_new.restype = ctypes.c_void_p
        libssl.SSL_CTX_free.argtypes = [ctypes.c_void_p]
        libssl.SSL_CTX_free.restype = None
        libssl.SSL_CTX_ctrl.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_long, ctypes.c_void_p]
        libssl.SSL_CTX_ctrl.restype = ctypes.c_long
        libssl.SSL_CTX_set_cipher_list.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        libssl.SSL_CTX_set_cipher_list.restype = ctypes.c_int
        libssl.SSL_CTX_set_psk_client_callback.argtypes = [ctypes.c_void_p, PSK_CLIENT_CALLBACK]
        libssl.SSL_CTX_set_psk_client_callback.restype = None
        libssl.SSL_new.argtypes = [ctypes.c_void_p]
        libssl.SSL_new.restype = ctypes.c_void_p
        libssl.SSL_free.argtypes = [ctypes.c_void_p]
        libssl.SSL_free.restype = None
        libssl.SSL_set_fd.argtypes = [ctypes.c_void_p, ctypes.c_int]
        libssl.SSL_set_fd.restype = ctypes.c_int
        libssl.SSL_connect.argtypes = [ctypes.c_void_p]
        libssl.SSL_connect.restype = ctypes.c_int
        libssl.SSL_read.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
        libssl.SSL_read.restype = ctypes.c_int
        libssl.SSL_write.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
        libssl.SSL_write.restype = ctypes.c_int
        libssl.SSL_shutdown.argtypes = [ctypes.c_void_p]
        libssl.SSL_shutdown.restype = ctypes.c_int
        libssl.SSL_get_error.argtypes = [ctypes.c_void_p, ctypes.c_int]
        libssl.SSL_get_error.restype = ctypes.c_int
        libssl.SSL_get_version.argtypes = [ctypes.c_void_p]
        libssl.SSL_get_version.restype = ctypes.c_char_p

        libcrypto.ERR_get_error.restype = ctypes.c_ulong
        libcrypto.ERR_error_string_n.argtypes = [ctypes.c_ulong, ctypes.c_char_p, ctypes.c_size_t]
        libcrypto.ERR_error_string_n.restype = None
        libcrypto.ERR_clear_error.restype = None
    except AttributeError as e:
        raise TLSError(
            'system OpenSSL is too old, version 1.1.0 or newer is required ({0})'.format(e))

    _libssl, _libcrypto = libssl, libcrypto
    return _libssl, _libcrypto


# unsigned int (*)(SSL *ssl, const char *hint, char *identity,
#                  unsigned int max_identity_len,
#                  unsigned char *psk, unsigned int max_psk_len)
PSK_CLIENT_CALLBACK = ctypes.CFUNCTYPE(
    ctypes.c_uint,
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_char),
    ctypes.c_uint,
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_uint)


def _errors():
    """Drain the OpenSSL error queue into a printable string."""
    _, libcrypto = _libs()
    messages = []
    while True:
        code = libcrypto.ERR_get_error()
        if code == 0:
            break
        buf = ctypes.create_string_buffer(256)
        libcrypto.ERR_error_string_n(code, buf, len(buf))
        messages.append(buf.value.decode('utf-8', 'replace'))
    return ', '.join(messages) or 'unknown error'


def _timeval(seconds):
    seconds = int(seconds)
    # struct timeval { time_t tv_sec; suseconds_t tv_usec; }
    return struct.pack('@ll', seconds, 0)


class OpenSSLSocket(object):
    """TLS-PSK connection over libssl, with the socket API the sender uses."""

    def __init__(self, sock, identity, psk, timeout, ciphers):
        libssl, _ = _libs()
        self._libssl = libssl
        self._sock = sock
        self._ssl = None
        self._ctx = None
        # OpenSSL does the I/O itself, so the socket must stay in blocking mode
        # and the timeout has to be enforced by the kernel
        sock.settimeout(None)
        if timeout:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, _timeval(timeout))
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, _timeval(timeout))

        identity = identity.encode('utf-8') if not isinstance(identity, bytes) else identity

        def psk_client_callback(_ssl, _hint, identity_buf, max_identity_len, psk_buf, max_psk_len):
            if len(identity) + 1 > max_identity_len or len(psk) > max_psk_len:
                return 0
            ctypes.memmove(identity_buf, identity + b'\0', len(identity) + 1)
            ctypes.memmove(psk_buf, psk, len(psk))
            return len(psk)

        # the callback must outlive the context, otherwise libssl calls freed memory
        self._callback = PSK_CLIENT_CALLBACK(psk_client_callback)

        ctx = libssl.SSL_CTX_new(libssl.TLS_client_method())
        if not ctx:
            raise TLSError('SSL_CTX_new failed: {0}'.format(_errors()))
        self._ctx = ctx
        libssl.SSL_CTX_ctrl(ctx, SSL_CTRL_SET_MIN_PROTO_VERSION, TLS1_2_VERSION, None)
        libssl.SSL_CTX_ctrl(ctx, SSL_CTRL_SET_MAX_PROTO_VERSION, TLS1_2_VERSION, None)
        if libssl.SSL_CTX_set_cipher_list(ctx, ciphers.encode('utf-8')) != 1:
            self.close()
            raise TLSError('no PSK cipher suite available for "{0}": {1}'.format(ciphers, _errors()))
        libssl.SSL_CTX_set_psk_client_callback(ctx, self._callback)

        ssl_obj = libssl.SSL_new(ctx)
        if not ssl_obj:
            self.close()
            raise TLSError('SSL_new failed: {0}'.format(_errors()))
        self._ssl = ssl_obj
        if libssl.SSL_set_fd(ssl_obj, sock.fileno()) != 1:
            self.close()
            raise TLSError('SSL_set_fd failed: {0}'.format(_errors()))
        ret = libssl.SSL_connect(ssl_obj)
        if ret != 1:
            error = self._describe(ret)
            self.close()
            raise TLSError('TLS handshake failed: {0}'.format(error))

    def version(self):
        if self._ssl is None:
            return None
        version = self._libssl.SSL_get_version(self._ssl)
        return version.decode('utf-8') if version else None

    def _describe(self, ret):
        code = self._libssl.SSL_get_error(self._ssl, ret)
        if code in (SSL_ERROR_WANT_READ, SSL_ERROR_WANT_WRITE):
            # the socket BIO reports the SO_RCVTIMEO/SO_SNDTIMEO expiry
            # as a retryable read/write, not as a syscall error
            return 'timed out'
        if code == SSL_ERROR_SYSCALL:
            errno = ctypes.get_errno()
            if errno in (11, 110):  # EAGAIN, ETIMEDOUT
                return 'timed out'
            return 'system error: {0}'.format(os.strerror(errno) if errno else 'connection closed')
        if code == SSL_ERROR_ZERO_RETURN:
            return 'connection closed by peer'
        return _errors()

    def sendall(self, data):
        buf = ctypes.create_string_buffer(bytes(data), len(data))
        sent, total = 0, len(data)
        while sent < total:
            written = self._libssl.SSL_write(
                self._ssl, ctypes.byref(buf, sent), total - sent)
            if written <= 0:
                raise TLSError('TLS write failed: {0}'.format(self._describe(written)))
            sent += written

    def recv(self, count):
        buf = ctypes.create_string_buffer(count)
        read = self._libssl.SSL_read(self._ssl, buf, count)
        if read < 0:
            raise TLSError('TLS read failed: {0}'.format(self._describe(read)))
        if read == 0:
            return b''
        return buf.raw[:read]

    def close(self):
        if self._ssl is not None:
            try:
                self._libssl.SSL_shutdown(self._ssl)
            except Exception:
                pass
            self._libssl.SSL_free(self._ssl)
            self._ssl = None
        if self._ctx is not None:
            self._libssl.SSL_CTX_free(self._ctx)
            self._ctx = None
        if self._sock is not None:
            self._sock.close()
            self._sock = None
