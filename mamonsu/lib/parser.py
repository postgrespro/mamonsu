# -*- coding: utf-8 -*-
import sys
from mamonsu import __version__
from optparse import OptionParser, BadOptionError
import mamonsu.lib.platform as platform
from mamonsu.lib.default_config import DefaultConfig

usage_msg = """
Options:
    -a, --add-plugins  <directory>
    -c, --config       <file>
    -p, --pid          <pid-file>
"""
if platform.LINUX:
    usage_msg += """    -d                 daemonize"""

usage_msg += """
        --version      output version information, then exit
        --help         show this help, then exit

Export example config with default variables:
Command: export
Examples:
    {prog} export config <file>
Options:
    --add-plugins <directory>
    
Export zabbix template with additional plugins included in config file:
Command: export template 
Examples:
    {prog} export template [options] <file>
Options:
    --add-plugins <directory>
    --template-name <template name> by default PostgresPro-<platform name>
    --application <application name in template> by default App-PostgresPro-<platform name>
    --config <file>
    --old-zabbix
HINT: By default, mamonsu exports the template for Zabbix 4.4 or higher.
To export a template for older Zabbix versions, use the --old-zabbix option.

Bootstrap DDL for monitoring:
Command: bootstrap
Examples:
    {prog} bootstrap -M <mamonsu_username>
HINT:  -M <mamonsu_username> is used to assign ownership of bootstrap queries
Options:
    -p, --port <PGPORT>
    -W <PGPASSWORD>
    -d, --dbname <DBNAME>
    -U, --username <USERNAME>
    --host <PGHOST>
   
Information about working mamonsu:
Command: agent
Examples:
    {prog} agent version
    {prog} agent metric-list
    {prog} agent metric-get <metric key>
Options:
    -c, --config <file>

Zabbix API toolbox:
Command: zabbix
Usage:
    {prog} zabbix template list
    {prog} zabbix template show <template name>
    {prog} zabbix template id <template name>
    {prog} zabbix template delete <template id>
    {prog} zabbix template export <file>
    {prog} zabbix host list
    {prog} zabbix host show <host name>
    {prog} zabbix host id <host name>
    {prog} zabbix host delete <host id>
    {prog} zabbix host create <host name> <hostgroup id> <template id> <ip>
    {prog} zabbix host info templates <host id>
    {prog} zabbix host info hostgroups <host id>
    {prog} zabbix host info graphs <host id>
    {prog} zabbix host info items <host id>
    {prog} zabbix hostgroup list
    {prog} zabbix hostgroup show <hostgroup name>
    {prog} zabbix hostgroup id <hostgroup name>
    {prog} zabbix hostgroup delete <hostgroup id>
    {prog} zabbix hostgroup create <hostgroup name>
    {prog} zabbix item error <host name>
    {prog} zabbix item lastvalue <host name>
    {prog} zabbix item lastclock <host name>
Options:
    --url=http://zabbix/web/face
    --user=WebUser
    --password=WebPassword
    
Export metrics to zabbix server
Command: upload
Example:
    {prog} upload --zabbix-address=localhost 
Options:    
    --zabbix-address <name of the Zabbix host to send metrics>
    --zabbix-port <port of Zabbix server to send metrics> by default 10051
    --zabbix-file <text file that stores the collected metric data to be visualized, such as localhost.log>
    --zabbix-client <name of the host on Zabbix Server to send metrics> 
    --zabbix-log-level <log level to send metrics> (INFO|DEBUG|WARN) by default INFO
"""

if platform.LINUX:
    usage_msg += """
Export zabbix keys for native zabbix-agent:
Command: export zabbix-parameters
Examples:
    {prog} export zabbix-parameters  <file>
Options:
    --plugin-type <plugin_type> (pg|sys|all) by default all
    --pg-version <pg_version> by default 10
    --add-plugins <directory>
    --config  <file>
HINT: Supported version numbers are 12, 10, 11, 9.6, 9.5

Export template for native zabbix agent:
Command: export zabbix-template
Examples:
    {prog} export zabbix-template [options] <file>
Options:
    --template-name <template name> by default PostgresPro-<platform name>
    --plugin-type <plugin_type> (pg|sys|all) by default all
    --application  <application name in template> by default App-PostgresPro-<platform name>
    --add-plugins <directory>
    --config  <file>
    --old-zabbix
By default, mamonsu exports the template for Zabbix 4.4 or higher.
To export a template for older Zabbix versions, use the --old-zabbix option.

Report about hardware and software:
Command: report
Options:
    --run-system=Boolean by default True
    --run-postgres=Boolean by default True
    --host <PGHOST>
    --port <PGPORT>
    --disable-sudo
    -W <PGPASSWORD>
    -d, --dbname <DBNAME>
    -U, --username <USERNAME>
    -r, --print-report
    -w, --report-path <path to file>
    
AutoTune config and system:
Command: tune
Options:
    -l, --log-level (INFO|DEBUG|WARN) by default INFO
    --dry-run
    --disable-sudo
    --dont-tune-pgbadger
    --dont-reload-postgresql
"""

if platform.WINDOWS:
    usage_msg += """
AutoTune config and system:
Command: tune
Options:
    -l, --log-level (INFO|DEBUG|WARN) by default INFO
    --dry-run
    --dont-tune-pgbadger
    --dont-reload-postgresql
"""


def print_total_help():
    print(usage_msg.format(prog=sys.argv[0]))
    sys.exit(2)


class MissOptsParser(OptionParser):

    def print_help(self, **kwargs):
        print("""

Export example config with default variables:
Command: export
Examples:
    {prog} export config <file> --add-plugins <directory>
Options:
    -c, --config <file>
    -p, --pid    <pid-file>
    -t, --template-name <template name> by default PostgresPro-<platform name>
    -a, --add-plugins <directory>


Export zabbix template with additional plugins included in config file:
Command: export
Examples:
    {prog} export template <file>
Options:
    --config <file>
    --template-name <template name> by default PostgresPro-<platform name>
    --application <application name in template> by default App-PostgresPro-<platform name>
    --add-plugins <directory>

Export zabbix keys for native zabbix-agent:
Command: export zabbix-parameters
Examples:
    {prog} export zabbix-parameters  <file>
Options:
    --pg-version <pg_version> by default 10
    --config <file>
    --add-plugins <directory>
HINT:  Supported version numbers are 12, 10, 11, 9.6, 9.5.

        
Export template for native zabbix agent:
Command: export zabbix-template 
Examples:
    {prog} export zabbix-template <file>
Options:
    --template-name <template name> by default PostgresPro-<platform name>
    --application <application name in template> by default App-PostgresPro-<platform name>
    --config <file>
    --add-plugins <directory>

""")
        sys.exit(2)

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

    def _add_help_option(self):
        self.add_option("--help",
                        action="help",
                        help="show this help message and exit")


def parse_args():
    parser = MissOptsParser(
        usage=usage_msg,
        version='%prog {0}'.format(__version__))
    parser.add_option(
        '-c', '--config', dest='config_file', default=DefaultConfig.default_config_path())
    # pid
    parser.add_option(
        '-p', '--pid', dest='pid', default=None)
    # daemonize
    parser.add_option(
        '-d', '--daemon', dest='daemon', action='store_true')
    # external plugins
    parser.add_option(
        '-a', '--add-plugins', dest='plugins_dirs', action='append')
    # template
    parser.add_option(
        '-t', '--template-name', dest='template',
        default='PostgresPro-{0}'.format(sys.platform.title()))

    parser.add_option('--plugin-type', dest='plugin_type',
                      default='all')
    # PG version
    parser.add_option('-v', '--pg-version', dest='pg_version',
                      default='10')
    parser.add_option(
        '--application', dest='application',
        default='App-PostgresPro-{0}'.format(sys.platform.title()))
    parser.add_option(
        '--old-zabbix',
        dest='old_zabbix', action='store_true',
        help='Create special template for currently unsupported zabbix versions')
    # Zabbix server to send metrics
    parser.add_option('--zabbix-address', dest='zabbix_address', default=None)
    # port of Zabbix server to send metrics
    parser.add_option('--zabbix-port', dest='zabbix_port', default='10051')
    # name of the Zabbix host to send metrics
    parser.add_option('--zabbix-client', dest='zabbix_client', default='localhost')
    # path to file with metrics to send metrics
    parser.add_option('--zabbix-file', dest='zabbix_file', default='/var/log/mamonsu/localhost.log')
    # log level to send metrics
    parser.add_option('--zabbix-log-level', dest='zabbix_log_level', default='INFO')
    return parser.parse_args()
