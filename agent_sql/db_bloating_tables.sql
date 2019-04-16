select count(*) from pg_catalog.pg_stat_all_tables where
                (n_dead_tup/(n_live_tup+n_dead_tup)::float8) > (0.2::float8)
                and (n_live_tup+n_dead_tup) > (50::integer)
