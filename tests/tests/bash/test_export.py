from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from src.core.docker import DockerManager
    from config.config import Config


class TestExportSuite:
    @pytest.mark.bash
    def test_export_config(self, mamonsu_container: 'DockerManager') -> None:
        exit_code, output = mamonsu_container("mamonsu export config mamonsu.conf --add-plugins=/etc/mamonsu/plugins")
        assert exit_code == 0
        exit_code, output = mamonsu_container("test -f mamonsu.conf")  # we use "test -f" because 'file' always return 0
        assert exit_code == 0

    @pytest.mark.bash
    def test_export_template(self, mamonsu_container: 'DockerManager') -> None:
        exit_code, output = mamonsu_container("mamonsu export template template.xml --add-plugins=/etc/mamonsu/plugins")
        assert exit_code == 0
        exit_code, output = mamonsu_container("test -f template.xml")
        assert exit_code == 0

    @pytest.mark.bash
    def test_export_zabbix_params(
            self,
            mamonsu_container: 'DockerManager',
            init_mamonsu_in_zbx,
            config: 'Config'
    ) -> None:
        exit_code, output = mamonsu_container("mamonsu export zabbix-parameters zabbix.conf"
                                              " --add-plugins=/etc/mamonsu/plugins --config=/etc/mamonsu/agent.conf"
                                              f" --pg-version={config.POSTGRES_VERSION}")
        assert exit_code == 0
        exit_code, output = mamonsu_container("test -f zabbix.conf")
        assert exit_code == 0

    @pytest.mark.bash
    def test_export_zabbix_template(self, mamonsu_container: 'DockerManager') -> None:
        exit_code, output = mamonsu_container('mamonsu export zabbix-template zabbix_template.xml'
                                              ' --template-name="mamonsu-zabbix" --add-plugins=/etc/mamonsu/plugins'
                                              ' --config=/etc/mamonsu/agent.conf')
        assert exit_code == 0
        exit_code, output = mamonsu_container("test -f zabbix_template.xml")
        assert exit_code == 0
