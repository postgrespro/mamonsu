from typing import TYPE_CHECKING

import pytest

from config.config import Config

if TYPE_CHECKING:
    from src.core.docker import DockerManager


class TestZabbixCliDashboardTemplateSuite:
    default_template = Config().DEFAULT_TEMPLATE

    @pytest.mark.bash
    def test_dashboard_upload(
            self,
            mamonsu_container: 'DockerManager',
            zabbix_options: str,
            init_mamonsu_in_zbx,
    ) -> None:
        exit_code, output = mamonsu_container(
            f'mamonsu zabbix {zabbix_options} dashboard upload "{self.default_template}" | grep "True\\|Mamonsu dashboard" || exit 11'
        )
        assert exit_code == 0

    @pytest.mark.bash
    def test_template_list(
            self,
            mamonsu_container: 'DockerManager',
            zabbix_options: str,
            init_mamonsu_in_zbx,
    ) -> None:
        exit_code, output = mamonsu_container(
            f'mamonsu zabbix {zabbix_options} template list | grep "{self.default_template}" || exit 11'
        )
        assert exit_code == 0

    @pytest.mark.bash
    def test_template_show(
            self,
            mamonsu_container: 'DockerManager',
            zabbix_options: str,
            init_mamonsu_in_zbx,
    ) -> None:
        exit_code, output = mamonsu_container(
            f'mamonsu zabbix {zabbix_options} template show "{self.default_template}" | grep "{self.default_template}" || exit 11'
        )
        assert exit_code == 0

    @pytest.mark.bash
    def test_template_id(
            self,
            mamonsu_container: 'DockerManager',
            zabbix_options: str,
            init_mamonsu_in_zbx,
    ) -> None:
        exit_code, output = mamonsu_container(
            f'mamonsu zabbix {zabbix_options} template id "{self.default_template}" | grep -x -E "[[:digit:]]+" || exit 11'
        )
        assert exit_code == 0

    @pytest.mark.bash
    def test_template_export_import(
            self,
            mamonsu_container: 'DockerManager',
            zabbix_options: str,
            init_mamonsu_in_zbx,
    ) -> None:
        exit_code, template_id = mamonsu_container(
            f'mamonsu zabbix {zabbix_options} template id "{self.default_template}"'
        )
        if exit_code == 0:
            mamonsu_container(f'mamonsu zabbix {zabbix_options} template delete {template_id.strip()}')

        exit_code, output = mamonsu_container(
            'mamonsu export template template.xml --template-name="mamonsu-zabbix"'
        )
        assert exit_code == 0

        exit_code, output = mamonsu_container(
            f'mamonsu zabbix {zabbix_options} template export template.xml'
        )
        assert exit_code == 0

        exit_code, output = mamonsu_container(
            f'mamonsu zabbix {zabbix_options} template id "mamonsu-zabbix" | grep -x -E "[[:digit:]]+" || exit 11'
        )
        assert exit_code == 0

        exit_code, template_id = mamonsu_container(
            f'mamonsu zabbix {zabbix_options} template id "mamonsu-zabbix"'
        )
        mamonsu_container(f'mamonsu zabbix {zabbix_options} template delete {template_id.strip()}')
        mamonsu_container('rm -rf template.xml')

    @pytest.mark.bash
    def test_template_delete(
            self,
            mamonsu_container: 'DockerManager',
            zabbix_options: str,
            init_mamonsu_in_zbx,
    ) -> None:
        mamonsu_container('mamonsu export template template.xml --template-name="test-template"')  # TODO: вынести
        mamonsu_container(f'mamonsu zabbix {zabbix_options} template export template.xml')

        exit_code, template_id = mamonsu_container(
            f'mamonsu zabbix {zabbix_options} template id "test-template"'
        )
        assert exit_code == 0
        template_id = template_id.strip()

        exit_code, output = mamonsu_container(
            f'mamonsu zabbix {zabbix_options} template delete {template_id} | grep "templateids.*{template_id}" || exit 11'
        )
        assert exit_code == 0

        mamonsu_container('rm -rf template.xml')
