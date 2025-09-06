from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from src.core.docker import DockerManager


class TestAgentSuite:
    @pytest.mark.parametrize(
        "command",
        (
                "",
                "-c /etc/mamonsu/agent.conf"
        )
    )
    @pytest.mark.bash
    def test_agent_version(self, mamonsu_container: 'DockerManager', init_mamonsu_in_zbx, command):
        exit_code, output = mamonsu_container(f"mamonsu agent version {command}")
        assert exit_code == 0

    @pytest.mark.parametrize(
        "command",
        (
                "",
                " -c /etc/mamonsu/agent.conf"
        )
    )
    @pytest.mark.bash
    def test_agent_metric_get_disk_all_read(self, mamonsu_container: 'DockerManager', init_mamonsu_in_zbx, command):
        exit_code, output = mamonsu_container(f"mamonsu agent metric-get system.disk.all_read[] {command}")
        assert exit_code == 0

    @pytest.mark.parametrize(
        "command",
        (
                "",
                " -c /etc/mamonsu/agent.conf"
        )
    )
    @pytest.mark.bash
    def test_agent_metric_list(self, mamonsu_container: 'DockerManager', init_mamonsu_in_zbx, command):
        exit_code, output = mamonsu_container(f"mamonsu agent metric-list {command}")
        assert exit_code == 0
