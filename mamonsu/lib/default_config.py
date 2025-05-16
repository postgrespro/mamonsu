# -*- coding: utf-8 -*-

import os
import logging
import os
import mamonsu.lib.platform as platform
if platform.WINDOWS:
    import win32api
else:
    import getpass


class PgsqlConfig(object):

    @staticmethod
    def default_user():
        if platform.WINDOWS:
            username = win32api.GetUserName()
        else:
            username = getpass.getuser()

        user = os.environ.get('PGUSER') or username or 'postgres'
        return user

    @staticmethod
    def default_pgpassword():
        password = os.environ.get('PGPASSWORD')
        return password

    @staticmethod
    def default_host():
        if platform.WINDOWS:
            host = os.environ.get('PGHOST') or 'localhost'
        if platform.LINUX:
            host = os.environ.get('PGHOST') or 'auto'
        if platform.FREEBSD:
            host = os.environ.get('PGHOST') or 'auto'
        if platform.DARWIN:
            host = os.environ.get('PGHOST') or 'auto'
        return host

    @staticmethod
    def default_port():
        port = int(os.environ.get('PGPORT') or 5432)
        return port

    @staticmethod
    def default_app():
        app = os.environ.get('PGAPPNAME') or 'mamonsu'
        return app

    @staticmethod
    def default_db():
        if platform.WINDOWS:
            username = win32api.GetUserName()
        else:
            username = getpass.getuser()

        database = os.environ.get('PGDATABASE') or os.environ.get('PGUSER') or username
        database = database or 'postgres'
        return database


class DefaultConfig(PgsqlConfig):

    @staticmethod
    def default_config_path():
        if platform.LINUX:
            return '/etc/mamonsu/agent.conf'
        elif platform.WINDOWS:
            return 'agent.conf'

    @staticmethod
    def get_logger_level(level):
        result = logging.INFO
        level = level.upper()
        if level == 'DEBUG':
            return logging.DEBUG
        if level == 'WARNING' or level == 'WARN':
            return logging.WARN
        return result

    @staticmethod
    def default_report_path():
        if platform.WINDOWS:
            return 'report.txt'
        if platform.LINUX:
            return '/tmp/report.txt'
