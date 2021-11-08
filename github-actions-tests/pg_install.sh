#!/bin/sh

# default parameters:
OS="centos:7"
PACKAGE_MANAGER_INSTALL="sudo yum -y install"
REPO=${PACKAGE_MANAGER_INSTALL}" https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm"
PG_VERSION="14"

for i in "$@"
do
case $i in
    --os=*)
    OS="${i#*=}"
    shift
    ;;
    --pmi=*)
    PACKAGE_MANAGER_INSTALL="${i#*=}"
    shift
    ;;
    --repo=*)
    REPO="${i#*=}"
    shift
    ;;
    --pg-version=*)
    PG_VERSION="${i#*=}"
    shift
    ;;
    *)
          # unknown option
    ;;
esac
done

echo && echo
echo "================================================================================================================="
echo "---> Install PostgreSQL ${PG_VERSION}"
echo && echo

# set up package name depending on distro
PACKAGE=""
PG_PATH=""
if [ "${OS%:*}" = "centos" ]; then
    PACKAGE="postgresql${PG_VERSION//./}-server postgresql${PG_VERSION//./}-contrib"
    PG_PATH="/usr/pgsql-${PG_VERSION}/bin/"
elif [ "${OS%:*}" = "ubuntu" ]; then
    PACKAGE="postgresql-${PG_VERSION} postgresql-contrib-${PG_VERSION}"
    PG_PATH="/usr/lib/postgresql/${PG_VERSION}/bin/"
fi

# set up recovery file name depending on PG version
RECOVERY_FILE="recovery.conf"
if [ "`echo "${PG_VERSION} >= 12" | bc`" -eq 1 ]; then
    RECOVERY_FILE="standby.signal"
fi

# install PostgreSQL
eval ${REPO}
eval "${PACKAGE_MANAGER_INSTALL} ${PACKAGE}"

# create PGDATA directories
sudo mkdir -p /pg${PG_VERSION}/data_master
sudo mkdir -p /pg${PG_VERSION}/data_slave_physical
sudo mkdir -p /pg${PG_VERSION}/wals
sudo chown -R postgres:postgres /pg${PG_VERSION}
sudo chmod 700 /pg${PG_VERSION}/data_master
sudo chmod 700 /pg${PG_VERSION}/data_slave_physical

# create master-slave cluster
sudo -u postgres ${PG_PATH}initdb -D /pg${PG_VERSION}/data_master/
sudo -u postgres echo "archive_mode=on" >> /pg${PG_VERSION}/data_master/postgresql.conf
sudo -u postgres echo "archive_command='cp %p /pg"${PG_VERSION}"/wals/%f'" >> /pg${PG_VERSION}/data_master/postgresql.conf
sudo -u postgres echo "wal_level=replica" >> /pg${PG_VERSION}/data_master/postgresql.conf
sudo -u postgres echo "max_wal_senders=4" >> /pg${PG_VERSION}/data_master/postgresql.conf
sudo -u postgres echo "hot_standby=on" >> /pg${PG_VERSION}/data_master/postgresql.conf
sudo -u postgres echo "host    replication     replicator      127.0.0.1/0             trust" >> /pg${PG_VERSION}/data_master/pg_hba.conf
sudo -u postgres ${PG_PATH}pg_ctl start -D /pg${PG_VERSION}/data_master/
sleep 3
sudo -u postgres ${PG_PATH}psql -c "CREATE DATABASE mamonsu_test_db;"
sudo -u postgres ${PG_PATH}psql -d mamonsu_test_db -c "CREATE TABLE mamonsu_test_table(id serial, value integer);"
sudo -u postgres ${PG_PATH}psql -d mamonsu_test_db -c "INSERT INTO mamonsu_test_table(value) SELECT * FROM generate_series(1, 10000);"
sudo -u postgres ${PG_PATH}psql -c "CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'secret';"
sudo -u postgres ${PG_PATH}pg_basebackup -h 127.0.0.1 -U replicator -Fp -Xs -P -R -D /pg${PG_VERSION}/data_slave_physical/
sudo -u postgres sed -i '/^archive_mode/s/^\(.*\)$/#\1/' /pg${PG_VERSION}/data_slave_physical/postgresql.conf
sudo -u postgres sed -i '/^archive_command/s/^\(.*\)$/#\1/' /pg${PG_VERSION}/data_slave_physical/postgresql.conf
sudo -u postgres echo "port=5433" >> /pg${PG_VERSION}/data_slave_physical/postgresql.conf
sudo -u postgres echo "restore_command = 'cp /pg"${PG_VERSION}"/wals/%f %p'" >> /pg${PG_VERSION}/data_slave_physical/${RECOVERY_FILE}
sudo -u postgres ${PG_PATH}pg_ctl start -D /pg${PG_VERSION}/data_slave_physical/

# create logical slave
if [ "`echo "${PG_VERSION} >= 10" | bc`" -eq 1 ]; then
    # create PGDATA directory
    sudo mkdir -p /pg${PG_VERSION}/data_slave_logical
    sudo chown postgres:postgres /pg${PG_VERSION}/data_slave_logical
    sudo chmod 700 /pg${PG_VERSION}/data_slave_logical

    sudo -u postgres sed -i '/^wal_level/s/^\(.*\)$/#\1/' /pg${PG_VERSION}/data_master/postgresql.conf
    sudo -u postgres echo "wal_level=logical" >> /pg${PG_VERSION}/data_master/postgresql.conf
    sudo -u postgres ${PG_PATH}pg_ctl restart -D /pg${PG_VERSION}/data_master/
    sleep 3
    sudo -u postgres ${PG_PATH}psql -c "GRANT ALL PRIVILEGES ON DATABASE mamonsu_test_db TO replicator;"
    sudo -u postgres ${PG_PATH}psql -d mamonsu_test_db -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO replicator;"
    sudo -u postgres ${PG_PATH}psql -d mamonsu_test_db -c "CREATE PUBLICATION mamonsu_publication;"
    sudo -u postgres ${PG_PATH}psql -d mamonsu_test_db -c "ALTER PUBLICATION mamonsu_publication ADD TABLE mamonsu_test_table;"
    sudo -u postgres ${PG_PATH}initdb -D /pg${PG_VERSION}/data_slave_logical/
    sudo -u postgres echo "host    all             all             127.0.0.1/0             trust" >> /pg${PG_VERSION}/data_slave_logical/pg_hba.conf
    sudo -u postgres echo "port=5434" >> /pg${PG_VERSION}/data_slave_logical/postgresql.conf
    sudo -u postgres ${PG_PATH}pg_ctl start -D /pg${PG_VERSION}/data_slave_logical/
    sleep 3
    sudo -u postgres ${PG_PATH}psql -p 5434 -c "CREATE DATABASE mamonsu_test_db;"
    sudo -u postgres ${PG_PATH}psql -p 5434 -d mamonsu_test_db -c "CREATE TABLE mamonsu_test_table(id serial, value integer);"
    sudo -u postgres ${PG_PATH}psql -p 5434 -d mamonsu_test_db -c "CREATE SUBSCRIPTION mamonsu_subscription CONNECTION 'host=127.0.0.1 port=5432 user=replicator dbname=mamonsu_test_db' PUBLICATION mamonsu_publication;"
fi
