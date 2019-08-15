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
from distutils.version import LooseVersion
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
        elif tool == 'export':
            args, commands = parse_args()
            # get PG version
            version_args = args.pg_version.split('_')
            define_pg_version(version_args)
            cfg = Config(args.config_file, args.plugins_dirs)
            if not len(commands) == 2 and not len(commands) == 3:
                print_total_help()
            if commands[1] == 'zabbix-parameters':
                # zabbix agent keys generation
                Plugin.Type = 'agent'  # change plugin type for template generator
                plugins = []
                if len(commands) == 2:
                    commands.append('postgrespro_agent.conf')
                    print('Configuration file for zabbix-agent have been saved in postgrespro_agent.conf file')
                for klass in Plugin.only_child_subclasses():
                    if klass.__name__ == "PgWaitSampling":  # check if plugin is for EE
                        if Plugin.VersionPG['type'] == 'PGEE':
                            plugins.append(klass(cfg))
                    else:
                        if klass.__name__ != "Cfs":
                            plugins.append(klass(cfg))
                args.plugin_type = correct_plugin_type(args.plugin_type)
                if args.plugin_type == 'pg' or args.plugin_type == 'sys' or args.plugin_type == 'all':
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
                        print("directory for scripts has created")
                    template = GetKeys()
                    # if no name for zabbix-parameters save to postgrespro.conf
                    if commands[2].rfind("/") == len(commands[2]) - 1:
                        commands[2] = commands[2][:-1] + "/postgrespro.conf"
                    # write conf file
                    with codecs.open(commands[2], 'w', 'utf-8') as f:
                        f.write(template.txt(args.plugin_type, plugins))  # pass command type
                    # write bash scripts for zabbix - agent to a file
                    for key in Scripts.Bash:
                        with codecs.open(path + "/" + key + ".sh", 'w+', 'utf-8') as f:
                            #   configuration file for zabbix-agent is generated for selected plugin-type
                            f.write(Scripts.Bash[key])  # pass script itself
                        os.chmod(path + "/" + key + ".sh", 0o755)
                    print("Bash scripts for native zabbix-agent have been saved to {0}".format(path))
                else:
                    print("Got wrong plugin types. For help, see the message below")
                    print_total_help()
                sys.exit(0)
            elif commands[1] == 'config':
                if len(commands) == 2:
                    commands.append('postgrespro.conf')
                    print('Configuration file for mamonsu have been saved in postgrespro.conf file')
                with open(commands[2], 'w') as fd:
                    cfg.config.write(fd)
                    sys.exit(0)
            elif commands[1] == 'template':
                plugins = []
                if len(commands) == 2:
                    commands.append('postgrespro.xml')
                    print('Template for mamonsu have been saved in postgrespro.conf file')
                for klass in Plugin.only_child_subclasses():
                    if klass.__name__ == "PgWaitSampling":  # check if plugin is for EE
                        if Plugin.VersionPG['type'] == 'PGEE':
                            plugins.append(klass(cfg))
                    else:
                        plugins.append(klass(cfg))
                template = ZbxTemplate(args.template, args.application)
                # if no name for template save to postgrespro.xml
                if commands[2].rfind("/") == len(commands[2]) - 1:
                    commands[2] = commands[2][:-1] + "/postgrespro.xml"
                with codecs.open(commands[2], 'w', 'utf-8') as f:
                    #   template for mamonsu (zabbix-trapper) is generated for all available plugins
                    f.write(template.xml("all", plugins))  # set type to 'all' for mamonsu
                    sys.exit(0)
            elif commands[1] == 'zabbix-template':
                Plugin.Type = 'agent'  # change plugin type for template generator
                if len(commands) == 2:
                    commands.append('postgrespro_agent.xml')
                    print('Template for zabbix-agent have been saved in postgrespro_agent.xml file')
                plugins = []
                args.plugin_type = correct_plugin_type(args.plugin_type)
                if args.plugin_type == 'pg' or args.plugin_type == 'sys' or args.plugin_type == 'all':
                    for klass in Plugin.only_child_subclasses():
                        if klass.__name__ == "PgWaitSampling":  # check if plugin is for EE
                            if Plugin.VersionPG['type'] == 'PGEE':
                                plugins.append(klass(cfg))
                        else:
                            if klass.__name__ != "Cfs":
                                plugins.append(klass(cfg))
                    template = ZbxTemplate(args.template, args.application)
                    # if no name for template save to postgrespro.xml
                    if commands[2].rfind("/") == len(commands[2]) - 1:
                        commands[2] = commands[2][:-1] + "/postgrespro.xml"
                    with codecs.open(commands[2], 'w', 'utf-8') as f:
                        #   template for zabbix-agent is generated for selected plugin-type
                        f.write(template.xml(args.plugin_type, plugins))
                    sys.exit(0)
                else:
                    print("Got wrong plugin types. For help, see the message below")
                    print_total_help()
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
def is_any_equal(iterator):
    length = len(iterator)
    return len(set(iterator)) < length


#  extract pg version from input
def define_pg_version(version_args):
    if len(version_args) == 1:
        if version_args[0] == "11" or LooseVersion(version_args[0]) == "10" or \
                LooseVersion(version_args[0]) == "9.6" or LooseVersion(version_args[0]) == "9.5":
            version_number = version_args[0].split('.')
            if len(version_number) > 3:
                print("Version number is too long. For help, see the message below")
                print_total_help()
            else:
                for num in version_number:
                    if not num.isdigit():
                        print("Version number contains only digits. For help, see the message below")
                        print_total_help()
                Plugin.VersionPG['number'] = version_args[0]
        else:
            print("Version number is not valid. For help, see the message below")
            print_total_help()
    elif len(version_args) == 2 and (version_args[0] == "PGEE" or version_args[0] == "PGPRO"):
        version_number = version_args[1].split('.')
        if len(version_number) > 3:
            print("Version number is too long. For help, see the message below")
            print_total_help()
        else:
            for num in version_number[1:]:
                if not num.isdigit():
                    print("Version number contains only digits. For help, see the message below")
                    print_total_help()
            if version_args[1] == "11" or LooseVersion(version_args[1]) == "10" or \
                    LooseVersion(version_args[1]) == "9.6" or LooseVersion(version_args[1]) == "9.5":
                Plugin.VersionPG['number'] = version_args[1]
                Plugin.VersionPG['type'] = version_args[0]
            else:
                print("Version number is not valid. For help, see the message below")
                print_total_help()
    else:
        print("Version number is not valid. For help, see the message below")
        print_total_help()


#  check if plugin type is valid
def correct_plugin_type(plugin_type):
    types = plugin_type.split(',')
    # if number of plugin types is more than 1 and plugin types are valid => plugin type should be 'all'
    valid_plugin_types = ('pg', 'sys', 'all')
    if len(types) == 2 or len(types) == 3:
        # check if any plugin types is equal
        if is_any_equal(types):
            print("Got equal plugin types. For help, see the message below")
            print_total_help()
        # if plugin type name is wrong
        if False in [type in valid_plugin_types for type in types]:
            print("Got wrong plugin types. For help, see the message below")
            print_total_help()
        else:
            plugin_type = 'all'
            return plugin_type
    elif len(types) > 3:
        print("Got more than 3 plugin types. For help, see the message below")
        print_total_help()
    else:
        return plugin_type
