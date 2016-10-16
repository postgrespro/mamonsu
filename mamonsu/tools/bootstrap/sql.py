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
    lsn = pg_catalog.pg_current_xlog_location()
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

CREATE OR REPLACE FUNCTION public.mamonsu_count_xlog_files()
RETURNS BIGINT AS $$
WITH list(filename) as (SELECT * FROM pg_catalog.pg_ls_dir('pg_xlog'))
SELECT
    COUNT(*)::BIGINT
FROM
    list
WHERE filename similar to '{2}'
$$ LANGUAGE SQL SECURITY DEFINER;
""".format(
    mamonsu_version,
    mamonsu_version.replace('.', '_'), '[0-9A-F]{24}')
