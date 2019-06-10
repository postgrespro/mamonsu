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

PATH = "/home/dvilova/Projects/mamonsu/"


def start():
    def quit_handler(_signo=None, _stack_frame=None):
        logging.info("Bye bye!")
        sys.exit(0)

    signal.signal(signal.SIGTERM, quit_handler)
    if platform.LINUX:
        signal.signal(signal.SIGQUIT, quit_handler)
    # temporal list to keep names of all refactored classes
    refactored_classes = ["Oldest", "PgBufferCache", "ArchiveCommand", "BgWriter", "Checkpoint", "Connections",
                           "Databases", "PgHealth", "Instance", "PgLocks", "Xlog",
                          "PgStatProgressVacuum", "PgStatStatement", "PgWaitSampling", "La", "OpenFiles",
                          "SystemUptime", "ProcStat"]
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
            if len(version_args) == 1:
                if "9.0" < LooseVersion(version_args[0]) < "12.0":
                    version_number = version_args[0].split('.')
                    if len(version_number) > 3:
                        print_total_help()
                    else:
                        for num in version_number:
                            if not num.isdigit():
                                print_total_help()
                        Plugin.VersionPG['number'] = version_args[0]
                else:
                    print_total_help()
            elif len(version_args) == 2 and (version_args[0] == "PGEE" or version_args[0] == "PGPRO"):
                version_number = version_args[1].split('.')
                if len(version_number) > 3:
                    print_total_help()
                else:
                    for num in version_number[1:]:
                        if not num.isdigit():
                            print_total_help()
                    if "9.0" < LooseVersion(version_args[1]) < "12.0":
                        Plugin.VersionPG['number'] = version_args[1]
                        Plugin.VersionPG['type'] = version_args[0]
                    else:
                        print_total_help()
            else:
                print_total_help()
            #print(Plugin.VersionPG['type'])
            #print(Plugin.VersionPG['number'])
            #print("this is args", args)
            #print("this is commands", commands)
            cfg = Config(args.config_file, args.plugins_dirs)
            if not len(commands) == 3:
                print_total_help()
            if commands[1] == 'zabbix-parameters':
                # zabbix agent keys generation
                Plugin.Type = 'agent'  # change plugin type for template generator
                plugins = []
                for klass in Plugin.only_child_subclasses():
                    if klass.__name__ in refactored_classes:
                        if klass.__name__ == "PgWaitSampling":   # check if plugin is for EE
                            if Plugin.VersionPG['type'] == 'PGEE':
                                plugins.append(klass(cfg))
                        else:
                            plugins.append(klass(cfg))
                #  export sql queries in separate directory
                file_path = os.path.join(PATH, args.directory_name)
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                    print("directory for sql queries  created")
                for klass in Plugin.only_child_subclasses():
                    # temporary generate template for agent for classes that have been refactored
                    if klass.__name__ in refactored_classes:
                        for i, j in klass(cfg).sql().items():
                            with codecs.open("{0}/{1}.{2}.sql".format(file_path, klass.__name__, i),
                                             'w', 'utf-8') as f:
                                f.write(j)
                directory_name_list = args.directory_name.split('/')
                if len(directory_name_list) > 1:
                    conf_path = '/'.join(directory_name_list[:-1]) + '/' + commands[2]
                else:
                    conf_path = commands[2]
                types = args.plugin_type.split(',')
                # check if any plugin types is equal
                if len(types) > 1:
                    if is_any_equal(types):
                        print_total_help()
                # if number of plugin types is more than 1 => plugin type should be 'all'
                if len(types) > 1:
                    args.plugin_type = 'all'
                if args.plugin_type == 'pg' or args.plugin_type == 'sys' or args.plugin_type == 'all':
                    template = GetKeys()
                    with codecs.open(conf_path, 'w', 'utf-8') as f:
                        f.write(template.txt(args.plugin_type, plugins))  # pass command type
                else:
                    print_total_help()
                sys.exit(0)
            elif commands[1] == 'config':
                with open(commands[2], 'w') as fd:
                    cfg.config.write(fd)
                    sys.exit(0)
            elif commands[1] == 'template':
                plugins = []
                for klass in Plugin.only_child_subclasses():
                    # temporary generate template for agent for classes that have been refactored
                    if klass.__name__ in refactored_classes:
                        if klass.__name__ == "PgWaitSampling":  # check if plugin is for EE
                            if Plugin.VersionPG['type'] == 'PGEE':
                                plugins.append(klass(cfg))
                        else:
                            plugins.append(klass(cfg))
                template = ZbxTemplate(args.template, args.application)
                with codecs.open(commands[2], 'w', 'utf-8') as f:
                    f.write(template.xml(plugins))
                    sys.exit(0)
            elif commands[1] == 'zabbix-template':
                Plugin.Type = 'agent'  # change plugin type for template generator
                plugins = []
                for klass in Plugin.only_child_subclasses():
                    if klass.__name__ in refactored_classes:
                        if klass.__name__ == "PgWaitSampling":  # check if plugin is for EE
                            if Plugin.VersionPG['type'] == 'PGEE':
                                plugins.append(klass(cfg))
                        else:
                            plugins.append(klass(cfg))
                template = ZbxTemplate(args.template,
                                       args.application)
                with codecs.open(commands[2], 'w', 'utf-8') as f:
                    f.write(template.xml(plugins))
                    sys.exit(0)
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
