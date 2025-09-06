import uuid
from typing import TYPE_CHECKING

import pytest

from config.constants.containers import ContainersEnum
from tests.conftest import mamonsu_container

if TYPE_CHECKING:
    from src.core.docker import DockerManager
    from src.services.zabbix import ZabbixManager


class TestZabbixCliHostSuite:
    @pytest.mark.bash
    def test_host_list(self, mamonsu_container: 'DockerManager', init_mamonsu_in_zbx, zabbix_options) -> None:
        exit_code, output = mamonsu_container(
            f"mamonsu zabbix {zabbix_options} host list"
        )
        assert exit_code == 0
        assert ContainersEnum.MAMONSU in output

    @pytest.mark.bash
    def test_host_show(self, mamonsu_container: 'DockerManager', init_mamonsu_in_zbx, zabbix_options) -> None:
        exit_code, output = mamonsu_container(
            f"mamonsu zabbix {zabbix_options} host show $(hostname) | grep $(hostname) || exit 11"
        )
        assert exit_code == 0

    @pytest.mark.bash
    def test_host_id(self, mamonsu_container: 'DockerManager', init_mamonsu_in_zbx, zabbix_options) -> None:
        exit_code, output = mamonsu_container(
            f'mamonsu zabbix {zabbix_options} host id $(hostname) | grep -x -E "[[:digit:]]+" || exit 11'
        )
        assert exit_code == 0

    @pytest.mark.parametrize(
        "params",
        (
                "templates",
                "hostgroups",
                "graphs",
                "items"
        )
    )
    @pytest.mark.bash
    def test_host_info(
            self,
            mamonsu_container: 'DockerManager',
            init_mamonsu_in_zbx,
            zabbix_options: str,
            zabbix: 'ZabbixManager',
            params,
    ) -> None:
        host_id = zabbix.get_host_id(mamonsu_container.hostname)
        exit_code, output = mamonsu_container(
            f"mamonsu zabbix {zabbix_options} host info {params} {host_id} | grep $(hostname) || exit 11"
        )
        assert exit_code == 0

    @pytest.mark.bash
    def test_host_create(
            self,
            mamonsu_container: 'DockerManager',
            init_mamonsu_in_zbx,
            zabbix: 'ZabbixManager',
            zabbix_options: str,
    ) -> None:
        new_host = 'test_create'
        hostgroup_id = zabbix.default_hostgroup_id
        template_id = zabbix.default_template_id

        exit_code, output = mamonsu_container(
            f"mamonsu zabbix {zabbix_options} host create {new_host!r} {hostgroup_id} {template_id} {mamonsu_container.ip_address}"
        )
        assert exit_code == 0

        exit_code, output = mamonsu_container(
            f'mamonsu zabbix {zabbix_options} host id {new_host!r} | grep -x -E "[[:digit:]]+" || exit 11'
        )
        assert exit_code == 0

    @pytest.mark.bash
    def test_host_delete(
            self,
            mamonsu_container: 'DockerManager',
            zabbix_options: str,
            init_mamonsu_in_zbx,
            zabbix: 'ZabbixManager',
    ) -> None:
        with zabbix as zbx:
            hostgroup_ids = zbx.list_hostgroups()[0]['groupid']
            template_ids = zbx.list_templates()[0]['templateid']

            host = zbx.create_host(str(uuid.uuid4()), [hostgroup_ids], [template_ids], mamonsu_container.ip_address)

            exit_code, output = mamonsu_container(
                f'mamonsu zabbix {zabbix_options} host delete {host} | grep "hostids.*{host}" || exit 11'
            )
            assert exit_code == 0
