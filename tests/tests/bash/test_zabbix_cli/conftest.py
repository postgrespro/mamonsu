import pytest
from typing import TYPE_CHECKING

from tests.conftest import mamonsu_container

if TYPE_CHECKING:
    from src.core.docker import DockerManager


@pytest.fixture()
def zabbix_options(mamonsu_container: 'DockerManager') -> str:
    mamonsu_env = mamonsu_container.env_vars
    zbx_web_url = mamonsu_env["ZABBIX_URL"]
    zbx_user = mamonsu_env["ZABBIX_USER"]
    zbx_password = mamonsu_env["ZABBIX_PASSWD"]

    return f"--url={zbx_web_url} --user={zbx_user} --password={zbx_password}"
