# -*- coding: utf-8 -*-

import logging
import re
from mamonsu.plugins.pgsql.pool import Pooler


class PostgresInfo(object):

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
                'synchronous_standby_names'
            ],
            'Memory': [
                'shared_buffers', 'huge_pages', 'work_mem',
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
    pg_catalog.pg_get_userbyid(d.datdba),
    pg_catalog.pg_encoding_to_char(d.encoding),
    d.datcollate,
    d.datctype,
    pg_catalog.array_to_string(d.datacl, E'\n'),
    t.spcname,
    pg_catalog.shobj_description(d.oid, 'pg_database')
from pg_catalog.pg_database d
  join pg_catalog.pg_tablespace t on d.dattablespace = t.oid
order by 2 desc """,
        ('name', 'size', 'owner', 'encoding', 'collate',
            'ctype', 'privileges', 'tablespace', 'description')
    )

    def __init__(self, args):
        self.args = args
        logging.info('Collect pg_setting info...')
        self.settings = self._collect_query(self.QueryPgSettings)
        logging.info('Collect database list...')
        self.dblist = self._collect_query(self.QueryDBList)
        logging.info('Collect biggest table...')
        self.biggest_tables = self._collect_biggest()

    def collect(self):
        info = self.printable_info()
        logging.error("\n{}\n".format(self.store_raw()))
        return info

    _suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

    def _humansize_bytes(self, nbytes):
        if nbytes == 0:
            return '0 B'
        i = 0
        while nbytes >= 1024 and i < len(self._suffixes)-1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s %s' % (f, self._suffixes[i])

    def _humansize(self, value):
        m = re.search('(\d+) (\S+)', value)
        if m is None:
            return value
        val, suff = m.group(1), m.group(2)
        val, suff = int(val), suff.upper()
        if suff == 'S':
            return value
        if suff == 'MS':
            return value
        if suff == 'B':
            return self._humansize_bytes(val)
        if suff == 'KB':
            return self._humansize_bytes(val*1024)
        if suff == '4KB':
            return self._humansize_bytes(val*1024*4)
        if suff == '8KB':
            return self._humansize_bytes(val*1024*8)
        if suff == '16KB':
            return self._humansize_bytes(val*1024*16)
        if suff == 'MB':
            return self._humansize_bytes(val*1024*1024)
        if suff == 'GB':
            return self._humansize_bytes(val*1024*1024*1024)
        if suff == 'TB':
            return self._humansize_bytes(val*1024*1024*1024*1024)
        return value

    def store_raw(self):
        def format_out(info, val):
            return "# {0} ##################################\n{1}\n".format(
                info, val)
        out = format_out('PG SETTINGS', self.settings)
        out += format_out('PG DBLIST', self.dblist)
        out += format_out('PG DBLIST', self.biggest_tables)
        return out

    def printable_info(self):

        def format_header(info):
            return "\n###### {0:20} ###########################\n".format(info)

        def format_out(key, val):
            return "{0:40s}|    {1}\n".format(key, val)

        out = ''
        for key in self.QueryPgSettings[2]:
            out += format_header(key)
            for row in self.settings:
                for name in self.QueryPgSettings[2][key]:
                    if row[0] == name:
                        val = row[1]
                        if row[2] is not None:
                            val += ' {0}'.format(row[2])
                            val = self._humansize(val)
                        out += format_out(
                            name, val)
        out += format_header('Database sizes')
        for i, row in enumerate(self.dblist):
            if i == 0:
                continue
            out += format_out(row[0], self._humansize(row[1]))
        out += format_header('Biggest tables')
        for i, key in enumerate(sorted(
                self.biggest_tables,
                key=self.biggest_tables.__getitem__,
                reverse=True)):
            if i > 20:
                break
            out += format_out(
                key, self._humansize_bytes(self.biggest_tables[key]))
        return out

    def _collect_query(self, query_desc):
        result = [query_desc[1]]
        try:
            for row in Pooler.query(query_desc[0]):
                result.append(row)
        except Exception as e:
            logging.error("Query {0} error: {1}".format(query_desc[0], e))
        return result

    def _collect_biggest(self):
        result = {}
        for info_dbs in Pooler.query('select datname \
                from pg_catalog.pg_database where datistemplate = false'):
            try:
                for info_sizes in Pooler.query("select n.nspname, c.relname, \
                        pg_catalog.pg_total_relation_size(c.oid) as size from \
                        pg_catalog.pg_class c \
                            left join pg_catalog.pg_namespace n \
                            on n.oid = c.relnamespace \
                        where c.relkind IN ('r','v','m','S','f','') \
                        order by size \
                        desc", info_dbs[0]):
                    table_name = '{0}.{1}.{2}'.format(
                        info_dbs[0], info_sizes[0], info_sizes[1])
                    result[table_name] = info_sizes[2]
            except Exception as e:
                logging.error("Connect to db {0} error: {1}".format(
                    info_dbs[0], e))
        return result
