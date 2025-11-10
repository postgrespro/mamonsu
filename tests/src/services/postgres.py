from contextlib import contextmanager

import psycopg2

from config.config import Config
from src.utils.logger import LoggerClass

config = Config()


class PostgresManager:
    def __init__(
            self,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD,
            dbname=config.POSTGRES_DB,
            host=config.POSTGRES_EXT_HOST,
            port=config.POSTGRES_EXT_PORT,
    ):
        self._logger = LoggerClass(self.__class__.__name__)
        self.conn_params = {
            "user": user,
            "dbname": dbname,
            "password": password,
            "host": host,
            "port": port,
        }

    @contextmanager
    def connect(self, dbname: str | None = None):
        params = self.conn_params.copy()
        if dbname:
            params["dbname"] = dbname
        conn = psycopg2.connect(**params)
        conn.autocommit = True
        try:
            yield conn
        finally:
            conn.close()

    def run_sql(self, sql: str, dbname: str | None = None) -> list[tuple]:
        with self.connect(dbname) as conn:
            with conn.cursor() as cur:
                self._logger.debug(f"EXECUTING SQL: {sql}")
                cur.execute(sql)
                if cur.description:
                    return cur.fetchall()
                return []

    def user_exists(self, username: str) -> bool:
        res = self.run_sql(f"SELECT 1 FROM pg_roles WHERE rolname = '{username}'")
        return bool(res)

    def drop_user(self, username: str, reassigned_to: str = "postgres"):
        if not self.user_exists(username):
            return
        dbs = self.run_sql("SELECT datname FROM pg_database WHERE datname NOT IN ('template0','template1')")
        for (db,) in dbs:
            self.run_sql(f"REASSIGN OWNED BY {username} TO {reassigned_to}", db)
            self.run_sql(f"DROP OWNED BY {username}", db)
        self.run_sql(f"DROP ROLE {username}")

    def create_user(self, username: str):
        self.run_sql(f"CREATE USER {username} SUPERUSER PASSWORD 'your_password'")

    def create_database(self, dbname: str, owner: str):
        self.run_sql(f"CREATE DATABASE {dbname} OWNER {owner}")

    def drop_database(self, dbname: str):
        self.run_sql(f"""
            SELECT pg_terminate_backend(pid) 
            FROM pg_stat_activity WHERE datname = '{dbname}' AND pid <> pg_backend_pid()
        """)
        self.run_sql(f"DROP DATABASE IF EXISTS {dbname}")

    def check_table_exists(self, table: str, schema: str = "mamonsu", dbname: str | None = None) -> bool:
        result = self.run_sql(
            f"SELECT 1 FROM information_schema.tables WHERE table_schema = '{schema}' AND table_name = '{table}'",
            dbname,
        )
        return bool(result)

    def check_function_exists(self, function: str, schema: str = "mamonsu", dbname: str | None = None) -> bool:
        result = self.run_sql(
            f"SELECT 1 FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace "
            f"WHERE p.proname = '{function}' AND n.nspname = '{schema}'",
            dbname,
        )
        return bool(result)
