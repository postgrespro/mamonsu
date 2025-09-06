from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from src.core.docker import DockerManager


class TestZabbixCliItemSuite:
    @pytest.mark.parametrize(
        "params",
        (
                "error",
                "lastvalue",
                "lastclock",
        )
    )
    @pytest.mark.bash
    def test_item(
            self,
            mamonsu_container: 'DockerManager',
            params: str,
            zabbix_options: str,
            init_mamonsu_in_zbx,
    ) -> None:
        exit_code, output = mamonsu_container(f"mamonsu zabbix {zabbix_options} item {params} $(hostname)")
        assert exit_code == 0
