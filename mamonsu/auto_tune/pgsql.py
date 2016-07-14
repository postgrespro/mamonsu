# -*- coding: utf-8 -*-

import os
import sys
import logging

import mamonsu.lib.platform as platform
from mamonsu.plugins.pgsql.pg8000.core import ProgrammingError
from mamonsu.plugins.pgsql.pool import Pooler


class AutoTune(object):

    def __init__(self, args):

        if not self._is_connection_work():
            logging.error('Can\'t connect to PostgreSQL')
            sys.exit(5)

        self.args = args
        self._memory()
        self._auto_vacuum()
        self._bgwriter()
        self._configure_pgbadger()
        logging.info('Auto-tune PostgreSQL config: completed')
        self._reload_config()

    def _memory(self):
        if platform.WINDOWS:
            logging.info("No memory config for windows")
            return
        sysmemory = self._get_total_mem()
        if sysmemory == 0:
            return

        self._run_query(
            "alter system set shared_buffers to '{0}'".format(
                self._humansize_and_round_bytes(sysmemory/4)))
        self._run_query(
            "alter system set effective_cache_size to '{0}'".format(
                self._humansize_and_round_bytes(3*sysmemory/4)))
        self._run_query(
            "alter system set work_mem to '{0}'".format(
                self._humansize_and_round_bytes(sysmemory/30)))
        self._run_query(
            "alter system set maintenance_work_mem to '{0}'".format(
                self._humansize_and_round_bytes(sysmemory/5)))

    def _auto_vacuum(self):
        self._run_query(
            "alter system set autovacuum_max_workers to 20")
        self._run_query(
            "alter system set autovacuum_analyze_scale_factor to 0.01")
        self._run_query(
            "alter system set autovacuum_vacuum_scale_factor to 0.02")
        self._run_query(
            "alter system set vacuum_cost_delay to 1")

    def _bgwriter(self):
        self._run_query(
            "alter system set bgwriter_delay to 10")
        self._run_query(
            "alter system set bgwriter_lru_maxpages to 800")

    def _configure_pgbadger(self):
        if not self.args.pgbadger:
            return
        self._run_query(
            "alter system set logging_collector to on")
        self._run_query(
            "alter system set log_filename to 'postgresql-%%a.log'")
        self._run_query(
            "alter system set log_checkpoints to on")
        self._run_query(
            "alter system set log_connections to on")
        self._run_query(
            "alter system set log_disconnections to on")
        self._run_query(
            "alter system set log_lock_waits to on")
        self._run_query(
            "alter system set log_temp_files to 0")
        self._run_query(
            "alter system set log_autovacuum_min_duration to 0")
        self._run_query(
            "alter system set log_line_prefix to \
                '%%t [%%p]: [%%l-1] db=%%d,user=%%u,app=%%a,client=%%h '")

    def _reload_config(self):
        if not self.args.reload_config:
            return
        logging.info('Reload config...')
        self._run_query('select pg_catalog.pg_reload_conf()')

    def _is_connection_work(self):
        try:
            Pooler.query('select 1')
            return True
        except Exception as e:
            logging.error('Test query error: {0}'.format(e))
            return False

    def _get_total_mem(self):
        if os.path.isfile('/proc/meminfo'):
            try:
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        data = line.split()
                        if not len(data) == 3:
                            continue
                        if data[0] == 'MemTotal:' and data[2] == 'kB':
                            return int(data[1]) * 1024
            except:
                logging.error('Can\'t read /proc/meminfo')
        return 0

    def _run_query(self, query='', exit_on_fail=True):
        try:
            Pooler.query(query)
        except ProgrammingError as e:
            if '{0}'.format(e) == 'no result set':
                return
        except Exception as e:
            logging.error('Query {0} error: {1}'.format(query, e))
            if exit_on_fail:
                sys.exit(6)

    def _humansize_and_round_bytes(self, nbytes):
        suffixes = ['', 'kB', 'MB', 'GB', 'TB']
        if nbytes < 1024:
            return str(nbytes)
        i = 0
        while nbytes >= 1024 and i < len(suffixes)-1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s%s' % (int(round(float(f))), suffixes[i])
