# -*- coding: utf-8 -*-

import logging
import optparse
import mamonsu.lib.platform as platform

from mamonsu import __version__
if platform.LINUX:
    from mamonsu.lib.first_look_os_linux import SystemInfo
else:
    from mamonsu.lib.first_look_os_win import SystemInfo


class Args(object):

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

        self.args, _ = parser.parse_args()
        logging.basicConfig(
            filename=self.args.report_path,
            level=self.get_logger_level(self.args.log_level))

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
