# -*- coding: utf-8 -*-

import logging
import time
from collections import OrderedDict
from mamonsu.plugins.pgsql.pool import Pooler
from mamonsu.tools.report.format import header_h1, key_val_h1, humansize


class PostgresInfo(object):

    QueryCommonInfo = (
        """
select
    version(),
    (now() - pg_postmaster_start_time())::time,
    round(sum(blks_hit)*100/sum(blks_hit+blks_read), 2)
from
    pg_catalog.pg_stat_database """,
        ('version', 'uptime', 'cache hit')
    )

    QueryConnections = (
        """
select count(*), 'total' from pg_catalog.pg_stat_activity
union all
select count(*), 'active' from pg_catalog.pg_stat_activity
    where state = 'active'
union all
select count(*), 'idle' from pg_catalog.pg_stat_activity where state = 'idle'
union all
select count(*), 'idle in transaction' from pg_catalog.pg_stat_activity
    where state = 'idle in transaction'
"""
    )

    QueryRate = (
        """
select
    date_part('epoch', now()),
    sum(xact_commit),
    sum(xact_rollback)
from pg_catalog.pg_stat_database
"""
    )

    QueryPgSettings = (
        """
select
    name,
    setting,
    unit,
    context,
    vartype,
    source,
    boot_val,
    reset_val
from pg_catalog.pg_settings """,
        ('name', 'setting', 'unit', 'context',
            'vartype', 'source', 'boot_val', 'reset_val'),
        ({
            'Data safe': [
                'fsync', 'synchronous_commit',
                'archive_command', 'synchronous_standby_names'
            ],
            'Memory': [
                'shared_buffers', 'huge_pages', 'work_mem',
                'maintenance_work_mem', 'autovacuum_work_mem',
                'temp_buffers', 'max_connections'
            ],
            'Autovacuum': [
                'autovacuum', 'autovacuum_max_workers',
                'autovacuum_naptime', 'autovacuum_vacuum_cost_delay',
                'autovacuum_analyze_scale_factor',
                'autovacuum_analyze_threshold',
                'autovacuum_vacuum_scale_factor',
                'autovacuum_vacuum_threshold'
            ],
            'BgWriter': [
                'bgwriter_delay',
                'bgwriter_lru_maxpages',
                'bgwriter_lru_multiplier'
            ],
            'KeepAlive': [
                'tcp_keepalives_count',
                'tcp_keepalives_idle',
                'tcp_keepalives_interval'
            ],
            'Libraries': [
                'shared_preload_libraries',
                'session_preload_libraries',
                'local_preload_libraries'
            ]
        })
    )

    QueryDBList = (
        """
select
    d.datname,
    case when pg_catalog.has_database_privilege(d.datname, 'CONNECT')
         then pg_catalog.pg_size_pretty(pg_catalog.pg_database_size(d.datname))
         else 'No Access'
    end,
    case when pg_catalog.has_database_privilege(d.datname, 'CONNECT')
         then pg_catalog.pg_database_size(d.datname)::text
         else 'No Access'
    end,
    pg_catalog.pg_get_userbyid(d.datdba),
    pg_catalog.pg_encoding_to_char(d.encoding),
    d.datcollate,
    d.datctype,
    pg_catalog.array_to_string(d.datacl, E'\n'),
    t.spcname,
    pg_catalog.shobj_description(d.oid, 'pg_database')
from pg_catalog.pg_database d
  join pg_catalog.pg_tablespace t on d.dattablespace = t.oid
order by 2""",
        ('name', 'size', 'size_b', 'owner', 'encoding', 'collate',
            'ctype', 'privileges', 'tablespace', 'description')
    )

    BigTableInfo = (
        """
with big_tables as (
    select
        c.oid as relid,
        c.relname,
        n.nspname as schema,
        pg_catalog.pg_total_relation_size(c.oid) as size
    from pg_catalog.pg_class c
    left join pg_catalog.pg_namespace n ON n.oid = c.relnamespace
    where c.relkind in ('r','v','m','S','f','')
        order by pg_catalog.pg_total_relation_size(c.oid) desc limit 10)
select
    b.schema || '.' || b.relname as "table",
    pg_catalog.pg_size_pretty(b.size) as "size",
    s.idx_scan,
    s.seq_scan,

    case s.n_live_tup when 0 then 0
        else round(100*s.n_mod_since_analyze::float8/s.n_live_tup::float8) end as "since_analyze_perc",

    case s.n_live_tup when 0 then 0
        else round(100*s.n_dead_tup::float8/s.n_live_tup::float8) end as "dead_perc",

    case coalesce(io.heap_blks_read + io.heap_blks_hit, 0) when 0 then 0
        else round(100*io.heap_blks_hit::float8/(io.heap_blks_read+io.heap_blks_hit)::float8) end as "heap_hit_perc",

    case coalesce(io.idx_blks_read + io.idx_blks_hit, 0) when 0 then 0
        else round(100*io.idx_blks_hit::float8/(io.idx_blks_read + io.idx_blks_hit)::float8) end as "idx_hit_perc",

    b.size as "size_b"

from
    pg_catalog.pg_stat_all_tables as s
    inner join pg_catalog.pg_statio_all_tables io on io.relid = s.relid
    inner join big_tables b on b.relid = s.relid
order by b.size desc
        """,
        ('table', 'size', 'idx-count', 'seq-count', '%-since-analyze',
            '%-dead', '%-heap-hit', '%-idx-hit')
    )

    def __init__(self, args):
        self.args = args
        logging.info('Test connection...')
        self.connected = self._is_connection_work()
        if not self.connected:
            return
        logging.info('Collect pg common info...')
        self.common_info = self._collect_query(self.QueryCommonInfo)
        logging.info('Collect rate.,.')
        self.rate = self._collect_rate()
        logging.info('Collect connection info...')
        self.connections = self._collect_connections()
        logging.info('Collect pg_setting info...')
        self.settings = self._collect_query(self.QueryPgSettings)
        logging.info('Collect database list...')
        self.dblist = self._collect_query(self.QueryDBList)
        logging.info('Collect biggest table...')
        self.biggest_tables = self._collect_biggest()

    def collect(self):
        info = self.printable_info()
        logging.error("\n{0}\n".format(self.store_raw()))
        return info.encode('ascii', 'ignore').decode('ascii')

    def _is_connection_work(self):
        try:
            Pooler.query('select 1')
            return True
        except Exception as e:
            logging.error('Test query error: {0}'.format(e))
            return False

    def store_raw(self):

        def format_obj(val):
            if val is None:
                return 'ERROR'
            if isinstance(val, list) or isinstance(val, tuple):
                result = ''
                for row in val:
                    result += format_obj(row)
                result += "\n"
                return result
            if isinstance(val, dict):
                result = ''
                for key in val:
                    result += '{0}:{1}\n'.format(key, format_obj(val[key]))
                return result
            return '{0:10}|'.format(val)

        def format_out(info, val):
            return "# {0} ##################################\n{1}\n".format(
                info, val)

        if not self.connected:
            out = format_out('Test connection', 'Failed')
            return out
        out = format_out('PG COMMON', format_obj(self.common_info))
        out += format_out('PG RATE', format_obj(self.rate))
        out += format_out('PG CONNECTIONS', format_obj(self.connections))
        out += format_out('PG SETTINGS', format_obj(self.settings))
        out += format_out('PG DBLIST', format_obj(self.dblist))
        out += format_out('TABLES LIST', format_obj(self.biggest_tables))
        return out

    def printable_info(self):

        def format_out(key, val):
            return "{0:40s}|    {1}\n".format(key, val)

        out = ''
        if not self.connected:
            out += header_h1('PGSQL Error')
            out += key_val_h1('Test connection', 'Failed')
            return out
        out += header_h1('PostgreSQL')
        out += key_val_h1('version', self.common_info[1][0])
        out += key_val_h1('uptime', self.common_info[1][1])
        out += key_val_h1('cache hit', '{0} %'.format(self.common_info[1][2]))
        out += key_val_h1('tps', self.rate['_TPS'])
        out += key_val_h1('rollbacks', self.rate['_ROLLBACKS'])
        out += header_h1('Connections')
        for info in self.connections:
            count, name = info
            out += key_val_h1(name, count)
        for key in self.QueryPgSettings[2]:
            out += header_h1(key)
            for row in self.settings:
                for name in self.QueryPgSettings[2][key]:
                    if row[0] == name:
                        val = row[1]
                        if row[2] is not None:
                            val += ' {0}'.format(row[2])
                            val = humansize(val)
                        out += key_val_h1(
                            name, val, 30)
        out += header_h1('Database sizes')
        for i, row in enumerate(self.dblist):
            if i == 0:
                continue
            out += key_val_h1(row[0], humansize(row[1]))
        out += header_h1('Biggest tables')
        out += key_val_h1(
            self.BigTableInfo[1][0],
            "\t\t" + "\t\t".join(self.BigTableInfo[1][1:]),
            30)
        for key in self.biggest_tables:
            out += key_val_h1(
                key, self.biggest_tables[key], 30)
        return out

    def _collect_query(self, query_desc):
        result = [query_desc[1]]
        try:
            for row in Pooler.query(query_desc[0]):
                result.append(row)
        except Exception as e:
            logging.error("Query {0} error: {1}".format(query_desc[0], e))
        return result

    def _collect_rate(self):
        result = {}
        result['_TPS'], result['_ROLLBACKS'] = '', ''
        try:
            result['row_1'] = Pooler.query(self.QueryRate)[0]
            time.sleep(2)
            result['row_2'] = Pooler.query(self.QueryRate)[0]
            exec_time = float(result['row_2'][0] - result['row_1'][0])
            result['_TPS'] = float(
                result['row_2'][1] - result['row_1'][1]) / exec_time
            result['_ROLLBACKS'] = float(
                result['row_2'][2] - result['row_1'][2]) / exec_time
        except Exception as e:
            logging.error('Query rate error: {0}'.format(e))
        return result

    def _collect_connections(self):
        result = []
        try:
            result = Pooler.query(self.QueryConnections)
        except Exception as e:
            logging.error('Query connections error: {0}'.format(e))
        return result

    def _collect_biggest(self):
        result, sizes, sorted_result = {}, {}, OrderedDict({})
        for info_dbs in Pooler.query('select datname \
                from pg_catalog.pg_database where datistemplate = false'):
            try:
                for info in Pooler.query(self.BigTableInfo[0], info_dbs[0]):
                    table_name = '{0}.{1}'.format(info_dbs[0], info[0])
                    result[table_name] = ''
                    values = info[1:]  # remove first elements (table name with schema)
                    sizes[table_name] = values.pop()  # size in bytes in last element
                    for val in values:
                        result[table_name] = "{0}\t\t{1}".format(
                            result[table_name], val)
            except Exception as e:
                logging.error("Connect to db {0} error: {1}".format(
                    info_dbs[0], e))
        for table_name in sorted(result, key=sizes.__getitem__, reverse=True):
            sorted_result[table_name] = result[table_name]
        return sorted_result
