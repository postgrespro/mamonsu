import os
import subprocess

import pytest
from docker.models.containers import Container

from config.config import Config
from config.constants.containers import ContainersEnum
from src.core.docker import DockerManager
from src.core.paths import ProjectPaths
from src.services.postgres import PostgresManager
from src.services.zabbix import ZabbixManager
from src.utils.logger import LoggerClass

logger = LoggerClass(__name__)


@pytest.fixture(scope="session")
def config() -> Config:
    return Config()


@pytest.fixture(scope="package")
def init_mamonsu_in_zbx(mamonsu_container: DockerManager) -> None:
    exit_code, _ = mamonsu_container('./app/init_mamonsu_in_zbx.sh')
    assert exit_code == 0, "Mamonsu initialization didn't complete successfully"


@pytest.fixture(scope="package")
def mamonsu_container(docker_compose) -> Container:  # noqa
    container = DockerManager(ContainersEnum.MAMONSU)
    yield container  # noqa
    container.stop()
    container.remove()


def parametrize(pg_version: int) -> int:
    os.environ["POSTGRES_VERSION"] = str(pg_version)
    return pg_version


@pytest.fixture(scope="session", params=[10, 11,
                                         # 12, 13, 14, 15, 16, 17
                                         ])
def docker_compose(config: Config, request) -> None:
    subprocess.run(
        ["docker", "rmi", f"{ContainersEnum.MAMONSU}:latest"]
    )

    os.environ["POSTGRES_VERSION"] = str(request.param)
    subprocess.run(
        [
            "docker-compose",
            "-f", ProjectPaths.COMPOSE_FILE,
            "--project-directory", ProjectPaths.MAMONSU_ROOT,
            "up",
            "-d",
            "--wait",
        ],
        # check=True,
    )
    yield  # noqa
    subprocess.run(
        [
            "docker-compose",
            "-f", ProjectPaths.COMPOSE_FILE,
            "--project-directory", ProjectPaths.MAMONSU_ROOT,
            "down",
        ],
        check=True,
    )


@pytest.fixture()
def zabbix() -> ZabbixManager:  # noqa
    zbx = ZabbixManager()
    yield zbx  # noqa
    zbx.remove_entities()


@pytest.fixture()
def postgres() -> PostgresManager:  # noqa
    yield PostgresManager()  # noqa
