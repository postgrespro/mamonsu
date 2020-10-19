# -*- coding: utf-8 -*-

import logging
import signal
import sys
import codecs
import os

import mamonsu.lib.platform as platform
from mamonsu.lib.parser import parse_args, print_total_help
from mamonsu.lib.config import Config
from mamonsu.lib.supervisor import Supervisor
from mamonsu.lib.plugin import Plugin
from mamonsu.lib.zbx_template import ZbxTemplate
from mamonsu.lib.get_keys import GetKeys

if platform.LINUX:
    from mamonsu.plugins.system.linux.scripts import Scripts


def start():
    def quit_handler(_signo=None, _stack_frame=None):
        logging.info("Bye bye!")
        sys.exit(0)

    signal.signal(signal.SIGTERM, quit_handler)
    if platform.LINUX:
        signal.signal(signal.SIGQUIT, quit_handler)

    commands = sys.argv[1:]
    if len(commands) > 0:
        tool = commands[0]
        if tool == '-h' or tool == '--help':
            print_total_help()
        elif tool == 'bootstrap':
            from mamonsu.tools.bootstrap.start import run_deploy
            sys.argv.remove('bootstrap')
            return run_deploy()
        elif tool == 'report':
            from mamonsu.tools.report.start import run_report
            sys.argv.remove('report')
            return run_report()
        elif tool == 'tune':
            from mamonsu.tools.tune.start import run_tune
            sys.argv.remove('tune')
            return run_tune()
        elif tool == 'zabbix':
            from mamonsu.tools.zabbix_cli.start import run_zabbix
            sys.argv.remove('zabbix')
            return run_zabbix()
        elif tool == 'agent':
            from mamonsu.tools.agent.start import run_agent
            sys.argv.remove('agent')
            return run_agent()
        elif tool == 'upload':
            args, commands = parse_args()
            if not args.zabbix_address:
                print('Option --zabbix-address is missing')
                sys.exit(2)
            if not os.path.isfile(args.zabbix_file):
                print('Cannot find zabbix file with metric to upload. Check path in --zabbix-file option.')
                sys.exit(2)

            cfg = Config(args.config_file, args.plugins_dirs)
            cfg.config.set('zabbix', 'address', args.zabbix_address)
            cfg.config.set('zabbix', 'port', args.zabbix_port)
            cfg.config.set('zabbix', 'client', args.zabbix_client)
            cfg.config.set('log', 'level', args.zabbix_log_level)

            supervisor = Supervisor(cfg)
            supervisor.send_file_zabbix(cfg, args.zabbix_file)
            sys.exit(0)

        elif tool == 'export':
            args, commands = parse_args()
            # get PG version
            Plugin.VersionPG = define_pg_version(args.pg_version)
            cfg = Config(args.config_file, args.plugins_dirs)
            if args.old_zabbix:
                Plugin.old_zabbix = True
            if not len(commands) == 2 and not len(commands) == 3:
                print_total_help()
            if commands[1] == 'zabbix-parameters':
                if platform.WINDOWS:
                    print("Export of zabbix keys for native zabbix-agent is not supported on Windows systems")
                    sys.exit(10)
                # zabbix agent keys generation
                Plugin.Type = 'agent'  # change plugin type for template generator
                plugins = []
                if len(commands) == 2:
                    commands.append('postgrespro_agent.conf')
                for klass in Plugin.only_child_subclasses():
                    if klass.__name__ != "PgWaitSampling" and klass.__name__ != "Cfs":
                        plugins.append(klass(cfg))
                args.plugin_type = correct_plugin_type(args.plugin_type)
                if args.plugin_type == 'pg' or args.plugin_type == 'sys' or args.plugin_type == 'all':
                    template = GetKeys()
                    # write conf file
                    try:
                        fd = codecs.open(commands[2], 'w', 'utf-8')
                        fd.write(template.txt(args.plugin_type, plugins))  # pass command type
                        print("Configuration file for zabbix-agent has been saved as {0}".format(commands[2]))
                    except (IOError, EOFError) as e:
                        print(" {0} ".format(e))
                        sys.exit(2)
                    # write bash scripts for zabbix - agent to a file
                    # check if conf file has a path
                    len_path = commands[2].rfind("/")
                    # get path for conf file and scripts
                    if len_path != -1:
                        path = commands[2][:len_path] + "/scripts"
                        Plugin.PATH = path
                    else:
                        path = os.getcwd() + "/scripts"
                        Plugin.PATH = path
                    # create directory for scripts along the path of conf file if needed
                    if not os.path.exists(path):
                        os.makedirs(path)
                    for key in Scripts.Bash:
                        with codecs.open(path + "/" + key + ".sh", 'w+', 'utf-8') as f:
                            #   configuration file for zabbix-agent is generated for selected plugin-type
                            f.write(Scripts.Bash[key])  # pass script itself
                        os.chmod(path + "/" + key + ".sh", 0o755)
                    print("Bash scripts for native zabbix-agent have been saved to {0}".format(path))
                else:
                    print("Got wrong plugin types. See help 'mamonsu -- help' ")
                    sys.exit(2)
                sys.exit(0)
            elif commands[1] == 'config':
                # if no name for conf, save to postgrespro.conf
                if len(commands) == 2:
                    commands.append('postgrespro.conf')
                try:
                    fd = open(commands[2], 'w')
                    cfg.config.write(fd)
                    print("Configuration file for mamonsu has been saved as {0}".format(commands[2]))
                    sys.exit(0)
                except (IOError, EOFError) as e:
                    print(" {0} ".format(e))
                    sys.exit(2)
            elif commands[1] == 'template':
                plugins = []
                if len(commands) == 2:
                    commands.append('postgrespro.xml')
                for klass in Plugin.only_child_subclasses():
                    plugins.append(klass(cfg))
                template = ZbxTemplate(args.template, args.application)
                try:
                    fd = codecs.open(commands[2], 'w', 'utf-8')
                    fd.write(template.xml("all", plugins))  # set type to 'all' for mamonsu
                    print('Template for mamonsu has been saved as {file}'.format(file=commands[2]))
                    sys.exit(0)
                except (IOError, EOFError) as e:
                    print(" {0} ".format(e))
                    sys.exit(2)
            elif commands[1] == 'zabbix-template':
                if platform.WINDOWS:
                    print("Export of template for native zabbix agent is not supported on Windows systems")
                    sys.exit(10)
                Plugin.Type = 'agent'  # change plugin type for template generator
                if len(commands) == 2:
                    commands.append('postgrespro_agent.xml')
                plugins = []
                args.plugin_type = correct_plugin_type(args.plugin_type)
                if args.plugin_type == 'pg' or args.plugin_type == 'sys' or args.plugin_type == 'all':
                    for klass in Plugin.only_child_subclasses():
                        if klass.__name__ != "PgWaitSampling" and klass.__name__ != "Cfs":  # check if plugin is for EE
                            plugins.append(klass(cfg))
                    template = ZbxTemplate(args.template, args.application)
                    try:
                        fd = codecs.open(commands[2], 'w', 'utf-8')
                        fd.write(template.xml(args.plugin_type, plugins))
                        print('Template for zabbix-agent has been saved as {file}'.format(file=commands[2]))
                        sys.exit(0)
                    except (IOError, EOFError) as e:
                        print(" {0} ".format(e))
                        sys.exit(2)
                else:
                    print("Got wrong plugin types. See help 'mamonsu -- help' ")
                    sys.exit(2)
            else:
                print_total_help()

    args, commands = parse_args()
    if len(commands) > 0:
        print_total_help()
    cfg = Config(args.config_file, args.plugins_dirs)

    # simple daemon
    if args.daemon:
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except Exception as e:
            sys.stderr.write('Can\'t fork: {0}\n'.format(e))
            sys.exit(2)

    # write pid-file
    if args.pid is not None:
        try:
            with open(args.pid, 'w') as pidfile:
                pidfile.write(str(os.getpid()))
        except Exception as e:
            sys.stderr.write('Can\'t write pid file, error: %s\n'.format(e))
            sys.exit(2)

    supervisor = Supervisor(cfg)

    try:
        logging.info("Start mamonsu")
        supervisor.start()
    except KeyboardInterrupt:
        quit_handler()


#  check if any equal elements in array
def is_any_equal(array):
    length = len(array)
    return len(set(array)) < length


#  extract pg version from input
def define_pg_version(version_args):
    if len(version_args) < 4:
        if version_args == "11" or version_args == "12" or version_args == "13" or version_args == "10" \
                or version_args == "9.6" or version_args == "9.5":
            version_number = version_args[0].split('.')
            for num in version_number:
                if not num.isdigit():
                    print("Version number contains only digits. See help 'mamonsu -- help' ")
                    sys.exit(2)
            return version_args
        else:
            print("Version number is not valid. See help 'mamonsu -- help' ")
            sys.exit(2)
    else:
        print("Version number is not valid. See help 'mamonsu -- help' ")
        sys.exit(2)


#  check if plugin type is valid
def correct_plugin_type(plugin_type):
    types = plugin_type.split(',')
    # if number of plugin types is more than 1 and plugin types are valid => plugin type should be 'all'
    valid_plugin_types = ('pg', 'sys', 'all')
    if len(types) == 2 or len(types) == 3:
        # check if any plugin types is equal
        if is_any_equal(types):
            print("Got equal plugin types. See help 'mamonsu -- help' ")
            sys.exit(2)
        # if plugin type name is wrong
        if False in [t in valid_plugin_types for t in types]:
            print("Got wrong plugin types. See help 'mamonsu -- help' ")
            sys.exit(2)
        else:
            plugin_type = 'all'
            return plugin_type
    elif len(types) > 3:
        print("Got more than 3 plugin types. See help 'mamonsu -- help' ")
        sys.exit(2)
    else:
        return plugin_type
