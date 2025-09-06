from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from src.core.docker import DockerManager
    from src.services.postgres import PostgresManager
    from config.config import Config


class TestZabbixCliDashboardTemplateSuite:
    @staticmethod
    def mamonsu_version(mamonsu_container: 'DockerManager') -> str:
        _, output = mamonsu_container(
            f'mamonsu --version'
        )
        version = output.split()[1].strip()
        version = version.replace(".", "_")
        return version

    @staticmethod
    def check_db_objects(pg: 'PostgresManager', dbname: str, version: str):
        assert pg.check_table_exists("config", dbname=dbname)
        assert pg.check_table_exists(f"timestamp_master_{version}", dbname=dbname)

        functions = [
            "archive_command_files", "archive_stat", "buffer_cache",
            "count_autovacuum", "count_wal_files", "count_wal_lag_lsn",
            # в оригинале может быть xlog вместо wal, но это актуально только для PG <10
            "get_connections_states", "get_oldest_transaction", "get_oldest_xid",
            "get_sys_param", "pg_buffercache_pages", "prepared_transaction",
            "timestamp_get", "timestamp_master_update"
        ]

        for func in functions:
            assert pg.check_function_exists(func, dbname=dbname)

    @pytest.mark.bash
    @pytest.mark.parametrize("db_name", ("mamonsu_test", "test_db"))
    def test_mamonsu_bootstrap_postgres(  # TODO: нужен тирдаун
            self,
            mamonsu_container: 'DockerManager',
            postgres: 'PostgresManager',
            config: 'Config',
            db_name: str
    ) -> None:
        postgres.drop_user("mamonsu")
        postgres.create_database(db_name, config.POSTGRES_USER)

        exit_code, _ = mamonsu_container(
            f'mamonsu bootstrap -x -U {config.POSTGRES_USER} -d {db_name} --password {config.POSTGRES_PASSWORD}'
        )
        assert exit_code == 0
        self.check_db_objects(postgres, db_name, self.mamonsu_version(mamonsu_container))

    @pytest.mark.bash
    def test_mamonsu_bootstrap_custom_user(
            self,
            mamonsu_container: 'DockerManager',
            postgres: 'PostgresManager',
    ):
        db = user = "test_superuser"
        postgres.drop_user("mamonsu")
        postgres.drop_database(db)
        postgres.drop_user(user)
        postgres.create_user(user)
        postgres.create_database(db, user)

        exit_code, _ = mamonsu_container(f"mamonsu bootstrap -x -U {user} -d {db}")
        assert exit_code == 0
        self.check_db_objects(postgres, db, self.mamonsu_version(mamonsu_container))

        postgres.drop_user("mamonsu")
        postgres.drop_user(user)
        postgres.drop_database(db)

    @pytest.mark.bash
    def test_mamonsu_bootstrap_custom_user_custom_host(
            self,
            mamonsu_container: 'DockerManager',
            postgres: 'PostgresManager'
    ):
        db = user = "test_superuser"
        postgres.drop_user("mamonsu")
        postgres.drop_database(db)
        postgres.drop_user(user)
        postgres.create_user(user)
        postgres.create_database(db, user)

        exit_code, _ = mamonsu_container(f"mamonsu bootstrap -x -U {user} -d {db} -h localhost -p 5432")
        assert exit_code == 0
        self.check_db_objects(postgres, db, self.mamonsu_version(mamonsu_container))

        postgres.drop_user("mamonsu")
        postgres.drop_user(user)
        postgres.drop_database(db)
