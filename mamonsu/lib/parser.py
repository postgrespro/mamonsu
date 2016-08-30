# -*- coding: utf-8 -*-
import sys
from mamonsu import __version__
from optparse import OptionParser, BadOptionError, SUPPRESS_HELP
import mamonsu.lib.platform as platform

usage_msg = """

Zabbix agent: %prog
Options:
    -c, --config <file>
    -p, --pid    <pid-file>
    -e <path to exported template>
        -t <template name>
        -a <application name>
    -w <path to exported config>


Api agent: %prog agent
Options:
    --config <file>
Examples:
    %prog agent version
    %prog agent metric-list
    %prog agent metric-get <metric key>


Zabbix cli: %prog zabbix
Options:
    --url=http://zabbix/web/face
    --user=WebUser
    --password=WebPassword
Examples:
    %prog zabbix template list
    %prog zabbix template show <template name>
    %prog zabbix template id <template name>
    %prog zabbix template delete <template id>
    %prog zabbix template export <file>
    %prog zabbix host list
    %prog zabbix host show <host name>
    %prog zabbix host id <host name>
    %prog zabbix host delete <host id>
    %prog zabbix host create <host name> <hostgroup id> <template id> <ip>
    %prog zabbix host info templates <host id>
    %prog zabbix host info hostgroups <host id>
    %prog zabbix host info graphs <host id>
    %prog zabbix host info items <host id>
    %prog zabbix hostgroup list
    %prog zabbix hostgroup show <hostgroup name>
    %prog zabbix hostgroup id <hostgroup name>
    %prog zabbix hostgroup delete <hostgroup id>
    %prog zabbix hostgroup create <hostgroup name>
    %prog zabbix item error <host name>
    %prog zabbix item lastvalue <host name>
    %prog zabbix item lastclock <host name>
"""


if platform.LINUX:
    usage_msg += """

Report: %prog report
Options:
    --run-system
    --run-postgres
    --host <PGHOST>
    --port <PGPORT>
    -W <PGPASSWORD>
    -d, --dbname <DBNAME>
    -U, --username <USERNAME>
    -r, --print-report
    -w, --report-path <path to file>


Tune: %prog tune
Options:
    -l, --log-level INFO|DEBUG|WARN
    --dry-run
    --disable-sudo
    --dont-tune-pgbadger
    --dont-reload-postgresql
"""


class MissOptsParser(OptionParser):

    def _process_long_opt(self, rargs, values):
        try:
            OptionParser._process_long_opt(self, rargs, values)
        except BadOptionError as err:
            self.largs.append(err.opt_str)

    def _process_short_opts(self, rargs, values):
        try:
            OptionParser._process_short_opts(self, rargs, values)
        except BadOptionError as err:
            self.largs.append(err.opt_str)


def parse_args():
    parser = MissOptsParser(
        usage=usage_msg,
        version='%prog {0}'.format(__version__))
    parser.add_option(
        '-c', '--config', dest='config_file', default=None,
        help=SUPPRESS_HELP)
    # pid
    parser.add_option(
        '-p', '--pid', dest='pid', default=None,
        help=SUPPRESS_HELP)
    # write config
    parser.add_option(
        '-w', dest='write_config_file', default=None,
        help=SUPPRESS_HELP)
    # template
    parser.add_option(
        '-e', dest='template_file', default=None,
        help=SUPPRESS_HELP)
    parser.add_option(
        '-t', dest='template',
        default='PostgresPro-{0}'.format(sys.platform.title()),
        help=SUPPRESS_HELP)
    parser.add_option(
        '-a', dest='application',
        default='App-PostgresPro-{0}'.format(sys.platform.title()),
        help=SUPPRESS_HELP)
    return parser.parse_args()
