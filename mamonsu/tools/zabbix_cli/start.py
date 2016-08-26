# -*- coding: utf-8 -*-

import os
import logging
import optparse

from mamonsu import __version__
from mamonsu.lib.default_config import DefaultConfig
from mamonsu.tools.zabbix_cli.operations import Operations


class Args(DefaultConfig):

    def __init__(self):

        parser = optparse.OptionParser(
            usage='%prog zabbix [--url] [--user] '
            '[--password] [--log-level] commands',
            version='%prog zabbix cli tools {0}'.format(__version__),
            description='Zabbix CLI tools')
        group = optparse.OptionGroup(
            parser,
            'Zabbix API connection settings')
        group.add_option(
            '--url',
            dest='zabbix_url',
            default=os.environ.get('ZABBIX_URL') or 'http://localhost/zabbix',
            help='URL of Zabbix Web interface (default: %default)')
        group.add_option(
            '--user',
            dest='zabbix_user',
            default=os.environ.get('ZABBIX_USER') or 'Admin',
            help='User (default: %default)')
        group.add_option(
            '--password',
            dest='zabbix_password',
            default=os.environ.get('ZABBIX_PASSWD') or 'zabbix',
            help='Password (default: %default)')
        group.add_option(
            '-l', '--log-level',
            dest='log_level',
            default='INFO', help='Log level (default: %default)')
        parser.add_option_group(group)

        self.args, commands = parser.parse_args()
        self.args.commands = commands

        # apply logging
        logging.basicConfig(
            level=self.get_logger_level(self.args.log_level))

    def __getattr__(self, name):
        try:
            return self.args.__dict__[name]
        except KeyError:
            return None


def run_zabbix():
    args = Args()
    Operations(args)
