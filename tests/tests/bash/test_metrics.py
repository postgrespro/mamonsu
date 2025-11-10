import time
from typing import TYPE_CHECKING

import pytest

from config.config import Config
from src.core.paths import ProjectPaths

if TYPE_CHECKING:
    from src.core.docker import DockerManager
    from src.services.postgres import PostgresManager


class TestMetricsSuite:
    @staticmethod
    def get_metrics_list():
        pg_ver = Config().POSTGRES_VERSION
        pg_ver = 14 if pg_ver == 15 else pg_ver  # We have no specific metric list for 15 ver of PG
        metrics_list = []
        with open(ProjectPaths.METRICS_PATH / f"metrics-linux-{pg_ver}.txt", 'r') as metrics_file:
            metrics_list = metrics_file.readlines()
        return metrics_list

    @pytest.mark.bash
    def test_metrics(
            self,
            mamonsu_container: 'DockerManager',
            init_mamonsu_in_zbx,
            postgres: 'PostgresManager'
    ) -> None:
        postgres.run_sql(
            """
            DO
            $do$
            DECLARE
               func_name varchar;
            BEGIN
               SELECT proname INTO func_name FROM pg_proc WHERE proname LIKE 'pg_switch_%';
               EXECUTE FORMAT('SELECT %s();', func_name);
            END
            $do$;
            """
        )
        time.sleep(120)
        bad_codes = []
        for metric in self.get_metrics_list():
            exit_code, output = mamonsu_container(
                f'mamonsu agent metric-get {metric.strip()} | grep "pgsql\|sys\|mamonsu"'
            )
            if exit_code != 0:
                bad_codes.append(metric)
        assert not bad_codes
