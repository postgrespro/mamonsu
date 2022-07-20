QuerySplit = """

"""

CreateMamonsuUserSQL = """
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles 
      WHERE rolname = '{0}') THEN
      CREATE ROLE {0} LOGIN PASSWORD '{0}';
   END IF;
END
$do$;

CREATE SCHEMA IF NOT EXISTS mamonsu;
ALTER SCHEMA mamonsu OWNER TO {0};
GRANT ALL PRIVILEGES ON SCHEMA mamonsu TO {0};
"""

CreateSchemaDefaultSQL = """
CREATE TABLE IF NOT EXISTS mamonsu.config (
  version text,
  inserted_at timestamp DEFAULT NOW()
);

INSERT INTO mamonsu.config(version) VALUES('{0}');

DROP TABLE IF EXISTS mamonsu.timestamp_master_{1};

CREATE TABLE mamonsu.timestamp_master_{1}(
    id int primary key,
    ts double precision,
    lsn pg_lsn
);

INSERT INTO mamonsu.timestamp_master_{1} (id) values (1);

DROP FUNCTION IF EXISTS mamonsu.timestamp_master_update();
CREATE OR REPLACE FUNCTION mamonsu.timestamp_master_update()
RETURNS void AS $$
  UPDATE mamonsu.timestamp_master_{1} SET
    ts = extract(epoch from now() at time zone 'utc')::double precision,
    lsn = pg_catalog.pg_current_{4}()
  WHERE
    id = 1;
$$ LANGUAGE SQL SECURITY DEFINER;

DROP FUNCTION IF EXISTS mamonsu.timestamp_get();
CREATE OR REPLACE FUNCTION mamonsu.timestamp_get()
RETURNS double precision AS $$
  SELECT
      CASE WHEN NOT pg_is_in_recovery() OR pg_last_{11}() = pg_last_{12}() THEN 0
      ELSE extract (epoch FROM now() - coalesce(pg_last_xact_replay_timestamp(), to_timestamp(ts)))
      END
  FROM mamonsu.timestamp_master_{1}
  WHERE id = 1 LIMIT 1;
$$ LANGUAGE SQL SECURITY DEFINER;

DO
$do$
BEGIN
   IF (SELECT setting::integer FROM pg_settings WHERE name = 'server_version_num') >= 100000 THEN
      DROP FUNCTION IF EXISTS mamonsu.count_autovacuum();
      CREATE OR REPLACE FUNCTION mamonsu.count_autovacuum()
      RETURNS BIGINT AS $$
         SELECT count(*)::bigint FROM pg_catalog.pg_stat_activity
         WHERE backend_type = 'autovacuum worker'
      $$ LANGUAGE SQL SECURITY DEFINER;
   ELSE
      DROP FUNCTION IF EXISTS mamonsu.count_autovacuum();
      CREATE OR REPLACE FUNCTION mamonsu.count_autovacuum()
      RETURNS BIGINT AS $$
         SELECT count(*)::bigint FROM pg_catalog.pg_stat_activity
         WHERE query LIKE '%%autovacuum%%'
         AND state <> 'idle'
         AND pid <> pg_catalog.pg_backend_pid()
      $$ LANGUAGE SQL SECURITY DEFINER;
   END IF;
END
$do$;

DO
$do$
BEGIN
   IF (SELECT setting::integer FROM pg_settings WHERE name = 'server_version_num') >= 100000 THEN
      DROP FUNCTION IF EXISTS mamonsu.autovacuum_utilization();
      CREATE OR REPLACE FUNCTION mamonsu.autovacuum_utilization()
      RETURNS FLOAT AS $$
         WITH count_tb AS (
            SELECT count(*)::float AS count
            FROM pg_catalog.pg_stat_activity
            WHERE backend_type = 'autovacuum worker'
         ),
         settings_tb AS (
            SELECT setting::float
            FROM pg_catalog.pg_settings
            WHERE name = 'autovacuum_max_workers'
         )
         SELECT count_tb.count*100/settings_tb.setting
         FROM count_tb, settings_tb
      $$ LANGUAGE SQL SECURITY DEFINER;
   ELSE
      DROP FUNCTION IF EXISTS mamonsu.count_autovacuum();
      CREATE OR REPLACE FUNCTION mamonsu.count_autovacuum()
      RETURNS FLOAT AS $$
         WITH count_tb AS (
            SELECT count(*)::float AS count
            FROM pg_catalog.pg_stat_activity
            WHERE query LIKE '%%autovacuum%%'
            AND state <> 'idle'
            AND pid <> pg_catalog.pg_backend_pid()
         ),
         settings_tb AS (
            SELECT setting::float
            FROM pg_catalog.pg_settings
            WHERE name = 'autovacuum_max_workers'
         )
         SELECT count_tb.count*100/settings_tb.setting
         FROM count_tb, settings_tb
      $$ LANGUAGE SQL SECURITY DEFINER;
   END IF;
END
$do$;

DO
$do$
BEGIN
   IF (SELECT setting::integer FROM pg_settings WHERE name = 'server_version_num') >= 100000 THEN
      DROP FUNCTION IF EXISTS mamonsu.get_connections_states();
      CREATE OR REPLACE FUNCTION mamonsu.get_connections_states()
      RETURNS TABLE(state text, waiting boolean) AS $$
         SELECT state,
                {5}
         FROM pg_catalog.pg_stat_activity
         WHERE (backend_type = 'client backend' OR backend_type = 'parallel worker')
      $$ LANGUAGE SQL SECURITY DEFINER;
   ELSE
      DROP FUNCTION IF EXISTS mamonsu.get_connections_states();
      CREATE OR REPLACE FUNCTION mamonsu.get_connections_states()
      RETURNS TABLE(state text, waiting boolean) AS $$
         SELECT state,
                {5}
         FROM pg_catalog.pg_stat_activity
         WHERE state is not null
      $$ LANGUAGE SQL SECURITY DEFINER;
   END IF;
END
$do$;

DROP FUNCTION IF EXISTS mamonsu.get_oldest_xid();
CREATE or REPLACE FUNCTION mamonsu.get_oldest_xid()
RETURNS BIGINT AS $$
    SELECT
        greatest(max(age(backend_xmin)),
        max(age(backend_xid)))::BIGINT
    FROM pg_catalog.pg_stat_activity
$$ LANGUAGE SQL SECURITY DEFINER;

DROP FUNCTION IF EXISTS mamonsu.get_oldest_transaction();
CREATE or REPLACE FUNCTION mamonsu.get_oldest_transaction()
RETURNS DOUBLE PRECISION AS $$
    SELECT 
        CASE WHEN extract(epoch from max(now() - xact_start)) IS NOT null 
              AND extract(epoch from max(now() - xact_start))>0
            THEN extract(epoch from max(now() - xact_start)) 
            ELSE 0 
        END 
    FROM pg_catalog.pg_stat_activity 
    WHERE 
        pid NOT IN(select pid from pg_stat_replication) AND 
        pid <> pg_backend_pid()
$$ LANGUAGE SQL SECURITY DEFINER;

DROP FUNCTION IF EXISTS mamonsu.count_{3}_files();
CREATE OR REPLACE FUNCTION mamonsu.count_{3}_files()
RETURNS BIGINT AS $$
WITH list(filename) as (SELECT * FROM pg_catalog.pg_ls_dir('pg_{3}'))
SELECT
    COUNT(*)::BIGINT
FROM
    list
WHERE filename similar to '{2}'
$$ LANGUAGE SQL SECURITY DEFINER;

DROP FUNCTION IF EXISTS mamonsu.archive_command_files();
CREATE OR REPLACE FUNCTION mamonsu.archive_command_files()
RETURNS TABLE(files_count BIGINT, files_size BIGINT) AS $$
WITH values AS (
SELECT
4096/(ceil(pg_settings.setting::numeric/1024/1024)) AS segment_parts_count,
setting::bigint AS segment_size,
('x' || substring(pg_stat_archiver.last_archived_wal from 9 for 8))::bit(32)::int AS last_wal_div,
('x' || substring(pg_stat_archiver.last_archived_wal from 17 for 8))::bit(32)::int AS last_wal_mod,
CASE WHEN pg_is_in_recovery() THEN NULL ELSE
('x' || substring(pg_{10}_name(pg_current_{4}()) from 9 for 8))::bit(32)::int END AS current_wal_div,
CASE WHEN pg_is_in_recovery() THEN NULL ELSE
('x' || substring(pg_{10}_name(pg_current_{4}()) from 17 for 8))::bit(32)::int END AS current_wal_mod
FROM pg_settings, pg_stat_archiver
WHERE pg_settings.name = 'wal_segment_size')
SELECT greatest(coalesce((segment_parts_count - last_wal_mod) + ((current_wal_div - last_wal_div - 1) * segment_parts_count) + current_wal_mod - 1, 0), 0)::bigint AS files_count,
greatest(coalesce(((segment_parts_count - last_wal_mod) + ((current_wal_div - last_wal_div - 1) * segment_parts_count) + current_wal_mod - 1) * segment_size, 0), 0)::bigint AS files_size
FROM values
$$ LANGUAGE SQL SECURITY DEFINER;

DROP FUNCTION IF EXISTS mamonsu.archive_stat();
CREATE OR REPLACE FUNCTION mamonsu.archive_stat()
RETURNS TABLE(archived_count BIGINT, failed_count BIGINT) AS $$
SELECT archived_count, failed_count from pg_stat_archiver
$$ LANGUAGE SQL SECURITY DEFINER;

DROP FUNCTION IF EXISTS mamonsu.get_sys_param(text);
CREATE OR REPLACE FUNCTION mamonsu.get_sys_param(param text)
RETURNS TABLE(SETTING TEXT) AS $$
select setting from pg_catalog.pg_settings where name = param
$$ LANGUAGE SQL SECURITY DEFINER;

DROP FUNCTION IF EXISTS mamonsu.prepared_transaction();
CREATE OR REPLACE FUNCTION mamonsu.prepared_transaction()
RETURNS TABLE(count_prepared BIGINT, oldest_prepared BIGINT) AS $$
SELECT COUNT(*) AS count_prepared,
coalesce (ROUND(MAX(EXTRACT (EPOCH FROM (now() - prepared)))),0)::bigint AS oldest_prepared  
FROM pg_catalog.pg_prepared_xacts$$ LANGUAGE SQL SECURITY DEFINER;

DROP FUNCTION IF EXISTS mamonsu.count_{3}_lag_lsn();
CREATE OR REPLACE FUNCTION mamonsu.count_{3}_lag_lsn()
RETURNS TABLE(application_name TEXT, {8} total_lag INTEGER) AS $$
SELECT application_name,
       {6} 
       coalesce((pg_{7}_diff(pg_current_{7}(), replay_{9}))::int, 0) AS total_lag
FROM pg_stat_replication
$$ LANGUAGE SQL SECURITY DEFINER;
"""

CreatePgBuffercacheFunctionsSQL = """
DO
$do$
DECLARE
	pg_buffercache_schema text;
BEGIN
    CREATE EXTENSION IF NOT EXISTS pg_buffercache WITH SCHEMA mamonsu;
    SELECT n.nspname INTO pg_buffercache_schema
    FROM pg_extension e
    JOIN pg_namespace n
    ON e.extnamespace = n.oid
    WHERE e.extname = 'pg_buffercache';
    EXECUTE 'DROP FUNCTION IF EXISTS mamonsu.buffer_cache();
CREATE OR REPLACE FUNCTION mamonsu.buffer_cache()
RETURNS TABLE(SIZE BIGINT, TWICE_USED BIGINT, DIRTY BIGINT) AS $$
SELECT
   SUM(1) * (current_setting(''block_size'')::int8),
   SUM(CASE WHEN usagecount > 1 THEN 1 ELSE 0 END) * (current_setting(''block_size'')::int8),
   SUM(CASE isdirty WHEN true THEN 1 ELSE 0 END) * (current_setting(''block_size'')::int8)
FROM ' || pg_buffercache_schema || '.pg_buffercache
$$ LANGUAGE SQL SECURITY DEFINER;';
END
$do$;
"""

CreateWaitSamplingFunctionsSQL = """
DO
$do$
DECLARE
    pg_type text;
	 extension_schema text;
BEGIN
   CREATE EXTENSION IF NOT EXISTS pgpro_stats WITH SCHEMA mamonsu;

   WITH tb_type AS (SELECT exists(SELECT * FROM pg_proc WHERE proname = 'pgpro_version'))
   SELECT
      CASE
         WHEN exists = false THEN 'vanilla' ELSE 'pro'
      END INTO pg_type
   FROM tb_type;

   <<functions_creation>>
   BEGIN
   IF pg_type = 'pro' THEN
      IF (SELECT EXISTS(SELECT * FROM pg_extension WHERE extname = 'pgpro_stats')) THEN
         SELECT n.nspname INTO extension_schema
         FROM pg_extension e
         JOIN pg_namespace n
         ON e.extnamespace = n.oid
         WHERE e.extname = 'pgpro_stats';   
         EXECUTE 'DROP FUNCTION IF EXISTS mamonsu.wait_sampling_all_locks();
         CREATE OR REPLACE FUNCTION mamonsu.wait_sampling_all_locks()
         RETURNS TABLE(lock_type text, count bigint) AS $$
            WITH lock_table AS (
            SELECT setoflocks.key,
                   json_data.key AS lock_type,
                   json_data.value::int AS count
            FROM (SELECT key, value AS locktuple
                  FROM jsonb_each((SELECT wait_stats
                                   FROM ' || extension_schema || '.pgpro_stats_totals
                                   WHERE object_type = ''cluster''))) setoflocks, 
            jsonb_each(setoflocks.locktuple) AS json_data)
            SELECT
                CASE
                    WHEN key = ''LWLockNamed'' THEN ''lwlock''
                    WHEN key = ''LWLockTranche'' THEN ''lwlock''
                    WHEN key = ''LWLock'' THEN ''lwlock''
                    WHEN key = ''Lock'' THEN ''hwlock''
                    WHEN key = ''BufferPin'' THEN ''buffer''
                    WHEN key = ''Extension'' THEN ''extension''
                    WHEN key = ''Client'' THEN ''client''
                    ELSE ''other''
                END,
                sum(count) AS count
            FROM lock_table
            WHERE key <> ''Total''
            GROUP BY 1
            ORDER BY count DESC;
         $$ LANGUAGE SQL SECURITY DEFINER;';
         EXECUTE 'DROP FUNCTION IF EXISTS mamonsu.wait_sampling_hw_locks();
         CREATE OR REPLACE FUNCTION mamonsu.wait_sampling_hw_locks()
         RETURNS TABLE(lock_type text, count bigint) AS $$
            WITH lock_table AS (
            SELECT setoflocks.key,
                   json_data.key AS lock_type,
                   json_data.value::int AS count
            FROM (SELECT key, value AS locktuple
                  FROM jsonb_each((SELECT wait_stats
                                   FROM ' || extension_schema || '.pgpro_stats_totals
                                   WHERE object_type = ''cluster''))) setoflocks, 
            jsonb_each(setoflocks.locktuple) AS json_data)
            SELECT
                lock_type,
                sum(count) AS count
            FROM lock_table
            WHERE key = ''Lock''
            GROUP BY 1
            ORDER BY count DESC;
         $$ LANGUAGE SQL SECURITY DEFINER;';
         EXECUTE 'DROP FUNCTION IF EXISTS mamonsu.wait_sampling_lw_locks();
         CREATE OR REPLACE FUNCTION mamonsu.wait_sampling_lw_locks()
         RETURNS TABLE(lock_type text, count bigint) AS $$
            WITH lock_table AS (
            SELECT setoflocks.key,
                   json_data.key AS lock_type,
                   json_data.value::int AS count
            FROM (SELECT key, value AS locktuple
                  FROM jsonb_each((SELECT wait_stats
                                   FROM ' || extension_schema || '.pgpro_stats_totals
                                   WHERE object_type = ''cluster''))) setoflocks, 
            jsonb_each(setoflocks.locktuple) AS json_data
            WHERE setoflocks.key IN (''Lock'', ''LWLock'', ''LWLockTranche'', ''LWLockNamed''))
            SELECT
                CASE
                    WHEN lock_type LIKE ''ProcArray%'' THEN ''xid''
                    WHEN lock_type LIKE ''Autovacuum%'' THEN ''autovacuum''
                    WHEN lock_type LIKE ''AutovacuumSchedule%'' THEN ''autovacuum''
                    WHEN lock_type LIKE ''WALBufMapping%'' THEN ''wal''
                    WHEN lock_type LIKE ''WALInsert%'' THEN ''wal''
                    WHEN lock_type LIKE ''WALWrite%'' THEN ''wal''
                    WHEN lock_type LIKE ''ControlFile%'' THEN ''wal''
                    WHEN lock_type = ''wal_insert'' THEN ''wal''
                    WHEN lock_type LIKE ''CLogControl%'' THEN ''clog''
                    WHEN lock_type LIKE ''CLogTruncation%'' THEN ''clog''
                    WHEN lock_type = ''clog'' THEN ''clog''
                    WHEN lock_type LIKE ''SyncRep%'' THEN ''replication''
                    WHEN lock_type LIKE ''ReplicationSlotAllocation%'' THEN ''replication''
                    WHEN lock_type LIKE ''ReplicationSlotControl%'' THEN ''replication''
                    WHEN lock_type LIKE ''ReplicationOrigin%'' THEN ''replication''
                    WHEN lock_type = ''replication_origin'' THEN ''replication''
                    WHEN lock_type = ''replication_slot_io'' THEN ''replication''
                    WHEN lock_type LIKE ''LogicalRepWorker%'' THEN ''logical_replication''
                    WHEN lock_type LIKE ''BufferContent%'' THEN ''buffer''
                    WHEN lock_type LIKE ''BufferMapping%'' THEN ''buffer''
                    WHEN lock_type = ''buffer_content'' THEN ''buffer''
                    WHEN lock_type = ''buffer_io'' THEN ''buffer''
                    WHEN lock_type = ''buffer_mapping'' THEN ''buffer''
                    ELSE ''other''
                END,
                sum(count) AS count
            FROM lock_table
            GROUP BY 1
            ORDER BY count DESC;
         $$ LANGUAGE SQL SECURITY DEFINER;';
      ELSE
         EXIT functions_creation;
      END IF;
   END IF;
   END functions_creation;
END
$do$;
"""

CreateStatementsFunctionsSQL = """
DO
$do$
DECLARE
    pg_type text;
    extension_schema text;
BEGIN
   CREATE EXTENSION IF NOT EXISTS pgpro_stats WITH SCHEMA mamonsu;

   WITH tb_type AS (SELECT exists(SELECT * FROM pg_proc WHERE proname = 'pgpro_version'))
   SELECT
      CASE
         WHEN exists = false THEN 'vanilla' ELSE 'pro'
      END INTO pg_type
   FROM tb_type;

   <<functions_creation>>
   BEGIN
   IF pg_type = 'pro' THEN
      IF (SELECT EXISTS(SELECT * FROM pg_extension WHERE extname = 'pgpro_stats')) THEN
         SELECT n.nspname INTO extension_schema
         FROM pg_extension e
         JOIN pg_namespace n
         ON e.extnamespace = n.oid
         WHERE e.extname = 'pgpro_stats';   
         EXECUTE 'DROP FUNCTION IF EXISTS mamonsu.statements_pro();
                  CREATE OR REPLACE FUNCTION mamonsu.statements_pro()
                  RETURNS TABLE({columns}) AS $$
                      SELECT {metrics}
                      FROM ' || extension_schema || '.pgpro_stats_totals
                      WHERE object_type = ''cluster'';        
                  $$ LANGUAGE SQL SECURITY DEFINER;';
      ELSE
         EXIT functions_creation;
      END IF;
   END IF;
   END functions_creation;
END
$do$;
"""

GrantsOnDefaultSchemaSQL = """
ALTER TABLE mamonsu.config OWNER TO {1};

ALTER TABLE mamonsu.timestamp_master_{0} OWNER TO {1};

GRANT EXECUTE ON FUNCTION mamonsu.timestamp_master_update() TO {1};

GRANT EXECUTE ON FUNCTION mamonsu.timestamp_get() TO {1};

GRANT EXECUTE ON FUNCTION mamonsu.count_autovacuum() TO {1};

GRANT EXECUTE ON FUNCTION mamonsu.get_oldest_xid() TO {1};

GRANT EXECUTE ON FUNCTION mamonsu.get_oldest_transaction() TO {1};

GRANT EXECUTE ON FUNCTION mamonsu.count_{2}_files() TO {1};

GRANT EXECUTE ON FUNCTION mamonsu.archive_command_files() TO {1};

GRANT EXECUTE ON FUNCTION mamonsu.archive_stat() TO {1};

GRANT EXECUTE ON FUNCTION mamonsu.get_sys_param(param text) TO {1};

GRANT EXECUTE ON FUNCTION mamonsu.get_connections_states() TO {1};

GRANT EXECUTE ON FUNCTION mamonsu.prepared_transaction() TO {1};

GRANT EXECUTE ON FUNCTION mamonsu.count_{2}_lag_lsn() TO {1};
"""

GrantsOnPgBuffercacheFunctionsSQL = """
GRANT EXECUTE ON FUNCTION mamonsu.buffer_cache() TO {1};
"""

GrantsOnWaitSamplingFunctionsSQL = """
DO
$do$
BEGIN
   IF (SELECT EXISTS(SELECT proname FROM pg_proc WHERE proname = 'wait_sampling_all_locks')) THEN
      EXECUTE 'GRANT EXECUTE ON FUNCTION mamonsu.wait_sampling_all_locks() TO {1};';
   END IF;
   IF (SELECT EXISTS(SELECT proname FROM pg_proc WHERE proname = 'wait_sampling_hw_locks')) THEN
      EXECUTE 'GRANT EXECUTE ON FUNCTION mamonsu.wait_sampling_hw_locks() TO {1};';
   END IF;
   IF (SELECT EXISTS(SELECT proname FROM pg_proc WHERE proname = 'wait_sampling_lw_locks')) THEN
      EXECUTE 'GRANT EXECUTE ON FUNCTION mamonsu.wait_sampling_lw_locks() TO {1};';
   END IF;
END
$do$;
"""

GrantsOnStatementsFunctionsSQL = """
DO
$do$
BEGIN
   IF (SELECT EXISTS(SELECT proname FROM pg_proc WHERE proname = 'statements_pro')) THEN
      EXECUTE 'GRANT EXECUTE ON FUNCTION mamonsu.statements_pro() TO {1};';
   END IF;
END
$do$;
"""
