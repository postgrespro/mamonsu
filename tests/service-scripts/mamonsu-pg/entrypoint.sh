#!/bin/bash
set -e

RECOVERY_FILE="standby.signal"

DATA_DIR=/var/lib/postgresql/data
DATA_SLAVE_PHYSICAL_DIR=/var/lib/postgresql/data_slave_physical
WAL_DIR=/var/lib/postgresql/wals
DATA_SLAVE_LOGICAL_DIR=/var/lib/postgresql/data_slave_logical

su postgres -c '/usr/local/bin/docker-entrypoint.sh postgres "$@" &'
sleep 5
su postgres -c "pg_ctl stop -D $DATA_DIR"

sudo mkdir -p $DATA_SLAVE_PHYSICAL_DIR
sudo mkdir -p $WAL_DIR
sudo chown -R postgres:postgres $DATA_SLAVE_PHYSICAL_DIR $WAL_DIR
sudo chmod 700 $DATA_SLAVE_PHYSICAL_DIR

sudo -u postgres echo "shared_preload_libraries = 'pg_stat_statements'" >> $DATA_DIR/postgresql.conf
sudo -u postgres echo "pg_stat_statements.track = all" >> $DATA_DIR/postgresql.conf
sudo -u postgres echo "archive_mode=on" >> $DATA_DIR/postgresql.conf
sudo -u postgres echo "archive_command='cp %p $WAL_DIR/%f'" >> $DATA_DIR/postgresql.conf
sudo -u postgres echo "wal_level=replica" >> $DATA_DIR/postgresql.conf
sudo -u postgres echo "max_wal_senders=4" >> $DATA_DIR/postgresql.conf
sudo -u postgres echo "hot_standby=on" >> $DATA_DIR/postgresql.conf

sudo -u postgres echo "track_io_timing = on" >> $DATA_DIR/postgresql.conf
sudo -u postgres echo "track_functions = all" >> $DATA_DIR/postgresql.conf

sudo -u postgres echo "host    replication     replicator      127.0.0.1/0             trust" >> $DATA_DIR/pg_hba.conf

su postgres -c "pg_ctl start -D $DATA_DIR"
sleep 3

sudo -u postgres psql -c "CREATE DATABASE mamonsu_test_db;"
sudo -u postgres psql -d mamonsu_test_db -c "CREATE EXTENSION pg_stat_statements;"
sudo -u postgres psql -d mamonsu_test_db -c "CREATE EXTENSION pg_buffercache;"
sudo -u postgres psql -d mamonsu_test_db -c "CREATE TABLE mamonsu_test_table(id serial, value integer);"
sudo -u postgres psql -d mamonsu_test_db -c "INSERT INTO mamonsu_test_table(value) SELECT * FROM generate_series(1, 10000);"
sudo -u postgres psql -c "CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'secret';"
sudo -u postgres pg_basebackup -h 127.0.0.1 -U replicator -Fp -Xs -P -R -D $DATA_SLAVE_PHYSICAL_DIR/
sudo -u postgres sed -i '/^archive_mode/s/^\(.*\)$/#\1/' $DATA_SLAVE_PHYSICAL_DIR/postgresql.conf
sudo -u postgres sed -i '/^archive_command/s/^\(.*\)$/#\1/' $DATA_SLAVE_PHYSICAL_DIR/postgresql.conf
sudo -u postgres echo "port=5433" >> $DATA_SLAVE_PHYSICAL_DIR/postgresql.conf
sudo -u postgres echo "restore_command = 'cp $WAL_DIR/%f %p'" >> $DATA_SLAVE_PHYSICAL_DIR/${RECOVERY_FILE}

su postgres -c "pg_ctl start -D $DATA_SLAVE_PHYSICAL_DIR"

# create logical slave
if [ "$POSTGRES_VERSION" -ge 100 ]; then  # TODO: Пофиксить, пока что отключено
    # create PGDATA directory
    sudo mkdir -p $DATA_SLAVE_LOGICAL_DIR
    sudo chown postgres:postgres $DATA_SLAVE_LOGICAL_DIR
    sudo chmod 700 $DATA_SLAVE_LOGICAL_DIR

    sudo -u postgres sed -i '/^wal_level/s/^\(.*\)$/#\1/' $DATA_DIR/postgresql.conf
    sudo -u postgres echo "wal_level=logical" >> $DATA_DIR/postgresql.conf
    su postgres -c "pg_ctl restart -D $DATA_DIR"
    sleep 3
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mamonsu_test_db TO replicator;"
    sudo -u postgres psql -d mamonsu_test_db -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO replicator;"
    sudo -u postgres psql -d mamonsu_test_db -c "CREATE PUBLICATION mamonsu_publication;"
    sudo -u postgres psql -d mamonsu_test_db -c "ALTER PUBLICATION mamonsu_publication ADD TABLE mamonsu_test_table;"
    sudo -u postgres echo "host    all             all             127.0.0.1/0             trust" >> $DATA_SLAVE_LOGICAL_DIR/pg_hba.conf
    sudo -u postgres echo "port=5434" >> $DATA_SLAVE_LOGICAL_DIR/postgresql.conf
    su postgres -c "pg_ctl start -D $DATA_SLAVE_LOGICAL_DIR"
    sleep 3
    sudo -u postgres psql -p 5434 -c "CREATE DATABASE mamonsu_test_db;"
    sudo -u postgres psql -p 5434 -d mamonsu_test_db -c "CREATE TABLE mamonsu_test_table(id serial, value integer);"
    sudo -u postgres psql -p 5434 -d mamonsu_test_db -c "CREATE SUBSCRIPTION mamonsu_subscription CONNECTION 'host=127.0.0.1 port=5432 user=replicator dbname=mamonsu_test_db' PUBLICATION mamonsu_publication;"
fi

mamonsu bootstrap -x --user postgres -d mamonsu_test_db
service mamonsu restart

tail -f /dev/null
