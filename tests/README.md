
# Mamonsu autotests

Mamonsu testing with different Postgres version, different operation systems(not supported yet). Uses docker-compose to run all services.


## Installation


```bash
  pip3 install -e requirement.txt
```

## Unit tests

The tests under `tests/unit` need neither docker nor a Zabbix server and are run from the repository root:

```bash
python -m pytest tests/unit
```

`tests/unit/test_tls_openssl.py` checks the TLS-PSK handshake against `openssl s_server`, so it is skipped when the openssl binary is missing. Both files can also be run directly with `python3`, which is handy on a host that has no pytest installed.

## Usage/Examples

You can simly run tests with only pytest mark "bash" and it will be ran with Postgres version from env variable POSTGRES_VERSION which is specified in .env file

```bash
pytest -m bash
```

You can run tests with different Postgres versions with  POSTGRES_VERSIONS variable

```bash
POSTGRES_VERSIONS=12,13 pytest -m bash
```

To run specific test you have to use -k flag with function name

```bash
POSTGRES_VERSIONS=12,13 pytest -k test_export_zabbix_params
```