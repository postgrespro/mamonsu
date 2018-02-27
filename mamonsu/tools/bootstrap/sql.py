from mamonsu import __version__ as mamonsu_version

QuerySplit = """

"""

CreateSchemaSQL = """
CREATE TABLE IF NOT EXISTS public.mamonsu_config (
  version text,
  inserted_at timestamp DEFAULT NOW()
);

INSERT INTO public.mamonsu_config(version) VALUES('{0}');

DROP TABLE IF EXISTS public.mamonsu_timestamp_master_{1};

CREATE TABLE public.mamonsu_timestamp_master_{1}(
    id int primary key,
    ts double precision,
    lsn pg_lsn
);

INSERT INTO public.mamonsu_timestamp_master_{1} (id) values (1);

CREATE OR REPLACE FUNCTION public.mamonsu_timestamp_master_update()
RETURNS void AS $$
  UPDATE public.mamonsu_timestamp_master_{1} SET
    ts = extract(epoch from now() at time zone 'utc')::double precision,
    lsn = pg_catalog.pg_current_{4}()
  WHERE
    id = 1;
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.mamonsu_timestamp_get()
RETURNS double precision AS $$
  SELECT
    (extract(epoch from now() at time zone 'utc') - ts)::double precision
  FROM public.mamonsu_timestamp_master_{1}
  WHERE id = 1 LIMIT 1;
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.mamonsu_count_autovacuum()
RETURNS BIGINT AS $$
    SELECT
        count(*)::BIGINT
    FROM pg_catalog.pg_stat_activity
    WHERE
        query like '%%autovacuum%%'
        and state <> 'idle'
        and pid <> pg_catalog.pg_backend_pid()
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.mamonsu_get_connections_states()
RETURNS TABLE(state text) AS $$
    SELECT
        state
    FROM pg_catalog.pg_stat_activity
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE or REPLACE FUNCTION public.mamonsu_get_oldest_xid()
RETURNS BIGINT AS $$
    SELECT
        greatest(max(age(backend_xmin)),
        max(age(backend_xid)))::BIGINT
    FROM pg_catalog.pg_stat_activity
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE or REPLACE FUNCTION public.mamonsu_get_oldest_query()
RETURNS DOUBLE PRECISION AS $$
    SELECT
        extract(epoch from max(now() - xact_start))
    FROM pg_catalog.pg_stat_activity
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.mamonsu_count_{3}_files()
RETURNS BIGINT AS $$
WITH list(filename) as (SELECT * FROM pg_catalog.pg_ls_dir('pg_{3}'))
SELECT
    COUNT(*)::BIGINT
FROM
    list
WHERE filename similar to '{2}'
$$ LANGUAGE SQL SECURITY DEFINER;

CREATE EXTENSION IF NOT EXISTS pg_buffercache;

CREATE OR REPLACE FUNCTION public.mamonsu_buffer_cache()
RETURNS TABLE(SIZE BIGINT, TWICE_USED BIGINT, DIRTY BIGINT) AS $$
SELECT
   SUM(1) * 8 * 1024,
   SUM(CASE WHEN usagecount > 1 THEN 1 ELSE 0 END) * 8 * 1024,
   SUM(CASE isdirty WHEN true THEN 1 ELSE 0 END) * 8 * 1024
FROM public.pg_buffercache
$$ LANGUAGE SQL SECURITY DEFINER;
"""

GrantsOnSchemaSQL = """
ALTER TABLE public.mamonsu_config OWNER TO {1};

ALTER TABLE public.mamonsu_timestamp_master_{0} OWNER TO {1};

GRANT EXECUTE ON FUNCTION public.mamonsu_timestamp_master_update() TO {1};

GRANT EXECUTE ON FUNCTION public.mamonsu_timestamp_get() TO {1};

GRANT EXECUTE ON FUNCTION public.mamonsu_count_autovacuum() TO {1};

GRANT EXECUTE ON FUNCTION public.mamonsu_get_oldest_xid() TO {1};

GRANT EXECUTE ON FUNCTION public.mamonsu_get_oldest_query() TO {1};

GRANT EXECUTE ON FUNCTION public.mamonsu_count_{2}_files() TO {1};

GRANT EXECUTE ON FUNCTION public.mamonsu_buffer_cache() TO {1};
"""
