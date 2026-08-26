# Encrypting the connection to Zabbix (mamonsu 3.5.17.1)

This document describes what changed compared to upstream **3.5.17**.

## Why

In 3.5.17 `ZbxSender` sends metrics to the Zabbix server over a plain TCP socket:

```python
sock = socket.socket()
sock.connect((self.host, self.port))
sock.sendall(packet)
```

When a host in Zabbix is set to **Connections from host: PSK**, the server rejects such connections and mamonsu cannot deliver a single metric, even though the stock `zabbix_sender` works with the same PSK settings.

Starting with 3.5.17.1 mamonsu encrypts the connection itself, with no external processes and no additional Python packages.

## What changed

| File | Change |
| --- | --- |
| `mamonsu/lib/senders/tls.py` | new module: the TLS-PSK and TLS-cert transports |
| `mamonsu/lib/senders/zbx.py` | reads the new settings and picks the transport in `_connect()` |
| `mamonsu/lib/config.py` | defaults for the `tls_*` parameters |
| `mamonsu/lib/parser.py`, `mamonsu/lib/runner.py` | the `--zabbix-tls-*` command line options |
| `packaging/conf/example_linux.conf` | commented example of the settings |
| `documentation/configuration_file.md` | description of the parameters |
| `tests/unit/` | tests that need neither docker nor a Zabbix server |

The wire format and the queue logic are untouched: `_send_data()` still sends `ZBXD\x01` + length + JSON. The only difference is where the socket comes from.

## Compatibility

**Without the new parameters the behaviour is exactly that of 3.5.17.** An existing `agent.conf` needs no changes: `tls_connect` defaults to `unencrypted`, and in that case the code path is the previous one.

If the settings are wrong (unknown mode, missing identity or key file, unreadable file), the sender is **disabled with an error in the log** instead of falling back to an unencrypted connection: mamonsu never quietly sends metrics in the clear.

## Configuring PSK

In `/etc/mamonsu/agent.conf`:

```ini
[zabbix]
address = zabbix-5
port = 10051
client = db2

tls_connect = psk
tls_psk_identity = PSK DB2
tls_psk_file = /etc/zabbix/zabbix_agentd.psk
```

`tls_psk_identity` and `tls_psk_file` have to match what is configured for this host in Zabbix (and the `TLSPSKIdentity` / `TLSPSKFile` of the Zabbix agent, if one runs on the same host).

How it works:

* on Python **3.13 and newer** — the standard `ssl` module (`SSLContext.set_psk_client_callback`);
* on Python **3.7 to 3.12** — a TLS client of our own through `ctypes` to the system libssl. Only the public OpenSSL API is used and no CPython internals are touched, so the same code works on Astra Linux 1.7.6 (OpenSSL 1.1.1, `libssl.so.1.1`) and Astra Linux 1.8 (OpenSSL 3.x, `libssl.so.3`).

A PSK connection is negotiated as **TLS 1.2**: TLS 1.3 carries the PSK through a different mechanism (`psk_use_session`), which is not implemented yet. Every Zabbix version that supports encryption accepts TLS 1.2.

## Configuring certificates

```ini
[zabbix]
tls_connect = cert
tls_ca_file = /etc/zabbix/ca.crt
tls_cert_file = /etc/zabbix/mamonsu.crt
tls_key_file = /etc/zabbix/mamonsu.key
# tls_crl_file = /etc/zabbix/ca.crl
# tls_server_cert_issuer = CN=Zabbix CA,O=Company
# tls_server_cert_subject = CN=zabbix server,O=Company
```

The server is validated the way the Zabbix agent does it: the chain is verified against the CA file, while the host name is **not** matched against the certificate — the server is pinned by its issuer and subject instead. Escaped commas in a DN are honoured (`CN=Company\, Inc`), the order of the attributes does not matter, and both short (`CN`, `O`, `OU`, `C`, ...) and long (`commonName`) names are accepted.

The `cert` mode works on any Python 3.x and uses the standard library only.

## Command line

Any of the settings except the cipher ones (`tls_cipher_psk`, `tls_cipher_cert`) can be overridden without touching the config file, which is convenient for checking a setup:

```bash
mamonsu -c /etc/mamonsu/agent.conf \
        --zabbix-tls-connect psk \
        --zabbix-tls-psk-identity 'PSK DB2' \
        --zabbix-tls-psk-file /etc/zabbix/zabbix_agentd.psk
```

The full list: `--zabbix-tls-connect`, `--zabbix-tls-psk-identity`, `--zabbix-tls-psk-file`, `--zabbix-tls-ca-file`, `--zabbix-tls-crl-file`, `--zabbix-tls-cert-file`, `--zabbix-tls-key-file`, `--zabbix-tls-server-cert-issuer`, `--zabbix-tls-server-cert-subject`. Only the options actually passed are overridden, the rest come from the config file. They work both for the daemon and for `mamonsu upload`.

## Security

* the PSK is read from the file once at startup and is kept in the memory of the process only;
* the content of the PSK file never reaches the log or the text of an error (there is a test for that);
* the PSK is not duplicated in `agent.conf`, which only holds the path to the file and the identity;
* the file has to be readable by the user mamonsu runs as (`mamonsu` in the systemd unit).

## Testing

The tests live in `tests/unit` and need neither docker nor Zabbix:

```bash
python -m pytest tests/unit                    # with pytest
python3 tests/unit/test_tls_openssl.py         # without it, e.g. on the monitored host
python3 tests/unit/test_zbx_sender_socket.py
```

What they cover:

* a real TLS handshake against `openssl s_server`, both PSK and certificates, with data going both ways;
* a wrong PSK, an unknown CA and a certificate subject that does not match are all rejected;
* parsing of the PSK file, and the absence of the secret in error messages;
* parsing and comparison of distinguished names;
* the unencrypted path: the frame is byte for byte the previous one and `failed: N` is still detected;
* the choice of the transport and the command line overrides.

Verified on Linux with Python 3.12 and OpenSSL 3.0.13 (the ctypes path) and on Windows with Python 3.12 (the cert mode on the standard library; the PSK tests are skipped there). On Astra Linux with OpenSSL 1.1.1 the code is the same but has not been run yet, so it is worth executing `test_tls_openssl.py` on the host itself.

The reference check with the stock utility:

```bash
zabbix_sender -c /etc/zabbix/zabbix_agent2.conf -z zabbix-5 -p 10051 -s db2 -k 'pgsql.ping[]' -o 1
# processed: 1; failed: 0; total: 1
```

After the settings are in place, mamonsu has to reach the same result without allowing `No encryption` on the Zabbix side.

## Known limitations

* TLS 1.3 with a PSK is not supported: the connection is pinned to TLS 1.2;
* the PSK file is read once at startup, so the agent has to be restarted after the key is changed;
* on Windows the `psk` mode requires Python 3.13 or newer, as there is no system libssl there;
* the `cert` mode has only been tested against `openssl s_server`, not against a production Zabbix server.

## Building

The version comes from `mamonsu/__init__.py`, and the same value is set in `packaging/debian/changelog` and `packaging/rpm/SPECS/mamonsu.spec` — `3.5.17.1`.

```bash
make -f Makefile.pkg deb
make -f Makefile.pkg rpm
```
