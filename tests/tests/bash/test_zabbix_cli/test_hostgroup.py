import uuid
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from src.core.docker import DockerManager
    from src.services.zabbix import ZabbixManager


class TestZabbixCliHostgroupSuite:
    @pytest.mark.bash
    def test_hostgroup_list(
            self,
            mamonsu_container: 'DockerManager',
            init_mamonsu_in_zbx,
            zabbix_options: str,
    ) -> None:
        exit_code, output = mamonsu_container(
            f"mamonsu zabbix {zabbix_options} hostgroup list | grep Linux || exit 11"
        )
        assert exit_code == 0

    @pytest.mark.bash
    def test_hostgroup_show(
            self,
            mamonsu_container: 'DockerManager',
            init_mamonsu_in_zbx,
            zabbix_options: str,
    ) -> None:
        exit_code, output = mamonsu_container(
            f'mamonsu zabbix {zabbix_options} hostgroup show "Linux servers" | grep Linux || exit 11'
        )
        assert exit_code == 0

    @pytest.mark.bash
    def test_hostgroup_id(
            self,
            mamonsu_container: 'DockerManager',
            init_mamonsu_in_zbx,
            zabbix_options: str,
    ) -> None:
        exit_code, output = mamonsu_container(
            f'mamonsu zabbix {zabbix_options} hostgroup id "Linux servers" | grep -x -E "[[:digit:]]+" || exit 11'
        )
        assert exit_code == 0

    @pytest.mark.bash
    def test_hostgroup_create(
            self,
            mamonsu_container: 'DockerManager',
            init_mamonsu_in_zbx,
            zabbix_options: str,
    ) -> None:
        exit_code, output = mamonsu_container(
            f'mamonsu zabbix {zabbix_options} hostgroup create "{str(uuid.uuid4())}"'
        )
        assert exit_code == 0

    @pytest.mark.bash
    def test_hostgroup_delete(
            self,
            mamonsu_container: 'DockerManager',
            init_mamonsu_in_zbx,
            zabbix_options: str,
            zabbix: 'ZabbixManager'
    ) -> None:
        hostgroup_id = zabbix.create_hostgroup("test")

        exit_code, output = mamonsu_container(
            f'mamonsu zabbix {zabbix_options} hostgroup delete {hostgroup_id} | grep "groupids.*{hostgroup_id}" || exit 11'
        )
        assert exit_code == 0
