# -*- coding: utf-8 -*-

import logging
import optparse
import os
import mamonsu.lib.platform as platform
from mamonsu.lib.default_config import DefaultConfig

from mamonsu import __version__
if platform.LINUX:
    from mamonsu.lib.first_look_os_linux import SystemInfo
else:
    from mamonsu.lib.first_look_os_win import SystemInfo


class Args(DefaultConfig):

    def __init__(self):

        parser = optparse.OptionParser(
            version='%prog first-look {0}'.format(__version__),
            description='First look report')
        group = optparse.OptionGroup(
            parser,
            'Start options')
        group.add_option(
            '-l', '--log-level',
            dest='log_level',
            default='INFO', help='Log level')
        parser.add_option_group(group)
        group = optparse.OptionGroup(
            parser,
            'Report options')
        group.add_option(
            '-w', '--report-path',
            dest='report_path',
            default='/tmp/results.txt', help='Path to report')
        group.add_option(
            '-r', '--print-report',
            dest='print_report',
            default=True, help='Print summary info')
        parser.add_option_group(group)
        group = optparse.OptionGroup(
            parser,
            'Postgres connection options')
        group.add_option(
            '-d', '--dbname',
            dest='dbname',
            default=self.default_db(), help='database name to connect to')
        group.add_option(
            '--host',
            dest='hostname',
            default=self.default_host(),
            help='database server host or socket full path')
        group.add_option(
            '-U', '--username',
            dest='username',
            default=self.default_user(),
            help='database user name')
        group.add_option(
            '-W', '--password',
            dest='password',
            default=self.default_user(),
            help='force password prompt (should happen automatically)')
        parser.add_option_group(group)

        self.args, _ = parser.parse_args()

        # apply logging
        logging.basicConfig(
            filename=self.args.report_path,
            level=self.get_logger_level(self.args.log_level))
        # apply env
        os.environ['PGUSER'] = self.args.username
        os.environ['PGPASSWORD'] = self.args.password
        os.environ['PGHOST'] = self.args.hostname
        os.environ['PGDATABASE'] = self.args.database
        os.environ['PGAPPNAME'] = 'mamonsu first look'

    def __getattr__(self, name):
        try:
            return self.args.__dict__[name]
        except KeyError:
            return None

    @staticmethod
    def get_logger_level(level):
        result = logging.INFO
        level = level.upper()
        if level == 'DEBUG':
            return logging.DEBUG
        if level == 'WARNING' or level == 'WARN':
            return logging.WARN
        return result


def run_first_look():
    args = Args()
    info = SystemInfo(args)
    info.run()
