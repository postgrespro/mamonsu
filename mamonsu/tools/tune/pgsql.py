# -*- coding: utf-8 -*-
import sys
import logging

import mamonsu.lib.platform as platform
from mamonsu.plugins.pgsql.pg8000.core import ProgrammingError
from mamonsu.plugins.pgsql.pool import Pooler
from mamonsu.tools.sysinfo.linux import SysInfoLinux as SysInfo


class AutoTunePgsl(object):

    def __init__(self, args):

        if not self._is_connection_work():
            logging.error('Can\'t connect to PostgreSQL')
            sys.exit(5)

        self.args = args
        self.sys_info = SysInfo()

        self._memory()
        self._auto_vacuum()
        self._bgwriter()
        self._configure_pgbadger()
        self._configure_extensions()

        self._reload_config()

    def _configure_extensions(self):

        extensions = self._run_query(
            "select name from pg_available_extensions")
        if extensions is None:
            return
        extensions = [row[0] for row in extensions]

        needed_libraries = []

        if 'pg_stat_statements' in extensions:
            needed_libraries.append('pg_stat_statements')
        else:
            logging.warning("Please install 'contrib' modules: need for 'pg_stat_statements'")

        if 'pg_wait_sampling' in extensions:
            needed_libraries.append('pg_wait_sampling')
        else:
            logging.warning("Install 'https://github.com/postgrespro/pg_wait_sampling' module'")

        if len(needed_libraries) == 0:
            return

        libraries = self._run_query('show shared_preload_libraries;')
        if libraries is None:
            return
        elif not len(libraries) == 1:
            return
        elif not len(libraries[0]) == 1:
            return

        libraries = libraries[0][0]
        if len(libraries) == 0:
            libraries = needed_libraries
        else:
            libraries = libraries.split(',')
            libraries = [ext.strip() for ext in libraries]
            if needed_libraries not in libraries:
                for ext in needed_libraries:
                    if ext not in libraries:
                        libraries.append(ext)
            libraries = ','.join(libraries)
        self._run_query(
            "alter system set shared_preload_libraries to {0};".format(
                libraries))

    def _memory(self):
        if platform.WINDOWS:
            logging.info('No memory tune for windows')
            return

        sysmemory = self.sys_info.meminfo['_TOTAL']
        if sysmemory == 0:
            return

        self._run_query(
            "alter system set shared_buffers to '{0}';".format(
                self._humansize_and_round_bytes(sysmemory / 4)))
        self._run_query(
            "alter system set effective_cache_size to '{0}';".format(
                self._humansize_and_round_bytes(3 * sysmemory / 4)))
        self._run_query(
            "alter system set work_mem to '{0}';".format(
                self._humansize_and_round_bytes(sysmemory / 100)))
        self._run_query(
            "alter system set maintenance_work_mem to '{0}';".format(
                self._humansize_and_round_bytes(sysmemory / 10)))

    def _auto_vacuum(self):
        self._run_query(
            "alter system set autovacuum_max_workers to 20;")
        self._run_query(
            "alter system set autovacuum_analyze_scale_factor to 0.01;")
        self._run_query(
            "alter system set autovacuum_vacuum_scale_factor to 0.02;")
        self._run_query(
            "alter system set vacuum_cost_delay to 1;")

    def _bgwriter(self):
        self._run_query(
            "alter system set bgwriter_delay to 10;")
        self._run_query(
            "alter system set bgwriter_lru_maxpages to 800;")

    def _configure_pgbadger(self):
        if self.args.pgbadger is not None:
            return
        self._run_query(
            "alter system set logging_collector to on;")
        self._run_query(
            "alter system set log_filename to 'postgresql-%%a.log';")
        self._run_query(
            "alter system set log_checkpoints to on;")
        self._run_query(
            "alter system set log_connections to on;")
        self._run_query(
            "alter system set log_disconnections to on;")
        self._run_query(
            "alter system set log_lock_waits to on;")
        self._run_query(
            "alter system set log_temp_files to 0;")
        self._run_query(
            "alter system set log_autovacuum_min_duration to 0;")
        self._run_query(
            "alter system set track_io_timing to on;")
        self._run_query(
            "alter system set log_line_prefix to "
            "'%%t [%%p]: [%%l-1] db=%%d,user=%%u,app=%%a,client=%%h ';")

    def _reload_config(self):
        if self.args.reload_config is not None:
            return
        self._run_query('select pg_catalog.pg_reload_conf();')

    def _is_connection_work(self):
        try:
            Pooler.query('select 1')
            return True
        except Exception as e:
            logging.error('Test query error: {0}'.format(e))
            return False

    def _run_query(self, query='', exit_on_fail=True):
        if self.args.dry_run:
            logging.info('dry run (query):\t{0}'.format(
                query.replace('%%', '%')))
            return None
        try:
            return Pooler.query(query)
        except ProgrammingError as e:
            if '{0}'.format(e) == 'no result set':
                return None
        except Exception as e:
            logging.error('Query {0} error: {1}'.format(query, e))
            if exit_on_fail:
                sys.exit(6)

    def _humansize_and_round_bytes(self, nbytes):
        suffixes = ['', 'kB', 'MB', 'GB', 'TB']
        if nbytes < 1024:
            return str(nbytes)
        i = 0
        while nbytes >= 1024 and i < len(suffixes) - 1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s%s' % (int(round(float(f))), suffixes[i])
