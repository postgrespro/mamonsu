

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

CREATE OR REPLACE FUNCTION mamonsu.timestamp_master_update()
RETURNS void AS $$
  UPDATE mamonsu.timestamp_master_{1} SET
    ts = extract(epoch from now() at time zone 'utc')::double precision,
    lsn = pg_catalog.pg_current_{4}()
  WHERE
    id = 1;
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE OR REPLACE FUNCTION mamonsu.timestamp_get()
RETURNS double precision AS $$
  SELECT
      CASE WHEN pg_last_{11}() = pg_last_{12}() THEN 0
      ELSE extract (epoch FROM now() - coalesce(pg_last_xact_replay_timestamp(), to_timestamp(ts)))
      END
  FROM mamonsu.timestamp_master_{1}
  WHERE id = 1 LIMIT 1;
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE OR REPLACE FUNCTION mamonsu.count_autovacuum()
RETURNS BIGINT AS $$
    SELECT
        count(*)::BIGINT
    FROM pg_catalog.pg_stat_activity
    WHERE
        query like '%%autovacuum%%'
        and state <> 'idle'
        and pid <> pg_catalog.pg_backend_pid()
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE OR REPLACE FUNCTION mamonsu.get_connections_states()
RETURNS TABLE(state text, waiting boolean) AS $$
    SELECT
        state,
        {5}
    FROM pg_catalog.pg_stat_activity
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE or REPLACE FUNCTION mamonsu.get_oldest_xid()
RETURNS BIGINT AS $$
    SELECT
        greatest(max(age(backend_xmin)),
        max(age(backend_xid)))::BIGINT
    FROM pg_catalog.pg_stat_activity
$$ LANGUAGE SQL SECURITY DEFINER;

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

CREATE OR REPLACE FUNCTION mamonsu.count_{3}_files()
RETURNS BIGINT AS $$
WITH list(filename) as (SELECT * FROM pg_catalog.pg_ls_dir('pg_{3}'))
SELECT
    COUNT(*)::BIGINT
FROM
    list
WHERE filename similar to '{2}'
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE OR REPLACE FUNCTION mamonsu.archive_command_files()
RETURNS TABLE(COUNT_FILES BIGINT, SIZE_FILES BIGINT) AS $$
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
SELECT greatest(coalesce((segment_parts_count - last_wal_mod) + ((current_wal_div - last_wal_div - 1) * segment_parts_count) + current_wal_mod - 1, 0), 0) AS count_files,
greatest(coalesce(((segment_parts_count - last_wal_mod) + ((current_wal_div - last_wal_div - 1) * segment_parts_count) + current_wal_mod - 1) * segment_size, 0), 0) AS size_files
FROM values
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE OR REPLACE FUNCTION mamonsu.archive_stat()
RETURNS TABLE(ARCHIVED_COUNT BIGINT, FAILED_COUNT BIGINT) AS $$
SELECT archived_count, failed_count from pg_stat_archiver
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE OR REPLACE FUNCTION mamonsu.get_sys_param(param text)
RETURNS TABLE(SETTING TEXT) AS $$
select setting from pg_catalog.pg_settings where name = param
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE OR REPLACE FUNCTION mamonsu.prepared_transaction()
RETURNS TABLE(count_prepared BIGINT, oldest_prepared BIGINT) AS $$
SELECT COUNT(*) AS count_prepared,
coalesce (ROUND(MAX(EXTRACT (EPOCH FROM (now() - prepared)))),0)::bigint AS oldest_prepared  
FROM pg_catalog.pg_prepared_xacts$$ LANGUAGE SQL SECURITY DEFINER;

CREATE OR REPLACE FUNCTION mamonsu.count_{3}_lag_lsn()
RETURNS TABLE(application_name TEXT, {8} total_lag NUMERIC ) AS $$
SELECT 
CONCAT(application_name, ' ', pid) as application_name,
{6} coalesce(pg_{7}_diff(pg_current_{7}(), replay_{9}), 0) AS total_lag 
FROM pg_stat_replication
$$ LANGUAGE SQL SECURITY DEFINER;
"""

CreateSchemaExtensionSQL = """
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
    EXECUTE 'CREATE OR REPLACE FUNCTION mamonsu.buffer_cache()
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

GrantsOnExtensionSchemaSQL = """
GRANT EXECUTE ON FUNCTION mamonsu.buffer_cache() TO {1};
"""
