
# Mamonsu autotests

Mamonsu testing with different Postgres version, different operation systems(not supported yet). Uses docker-compose to run all services.


## Installation


```bash
  pip3 install -e requirement.txt
```

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