/*select sum(res.compressed_size)/sum(res.compressed_size*res.ratio)*/
select sum(res.compressed_size)
from (
    select
        n.nspname || '.' || c.relname as table_name,
        /*cfs_compression_ratio(c.oid::regclass) as ratio,*/
        (pg_catalog.pg_total_relation_size(c.oid::regclass) - pg_catalog.pg_indexes_size(c.oid::regclass)) as compressed_size
    from
        pg_catalog.pg_class as c
        left join pg_catalog.pg_namespace n on n.oid = c.relnamespace
    where c.reltablespace in (select oid from pg_catalog.pg_tablespace where spcoptions::text ~ 'compression')
        and c.relkind IN ('r','v','m','S','f','p','')
       /*and cfs_compression_ratio(c.oid::regclass) <> 'NaN'*/

    union all

    select
        n.nspname || '.' || c.relname as table_name,
       /* cfs_compression_ratio(c.oid::regclass) as ratio,*/
        pg_catalog.pg_total_relation_size(c.oid::regclass) as compressed_size -- pg_toast included
    from
        pg_catalog.pg_class as c
        left join pg_catalog.pg_namespace n on n.oid = c.relnamespace
    where c.reltablespace in (select oid from pg_catalog.pg_tablespace where spcoptions::text ~ 'compression')
        and c.relkind = 'i'
       /* and cfs_compression_ratio(c.oid::regclass) <> 'NaN'*/

    ) AS res;

 SELECT count(name) AS count_files , coalesce(sum((pg_stat_file('./pg_{0}/' ||  rtrim(ready.name,'.ready'))).size),0) AS size_files FROM (SELECT name FROM pg_ls_dir('./pg_{0}/archive_status') name WHERE right( name,6)= '.ready'  ) ready;