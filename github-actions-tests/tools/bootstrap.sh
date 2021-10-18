#!/bin/sh

# 'mamonsu bootstrap' tool testing

# Requirements:
# - superuser for psql commands;
# - trust method for all users in pg_hba;

echo && echo
echo "================================================================================================================="
echo "---> Test MAMONSU BOOTSTRAP tool"
echo && echo

MAMONSU_FULL_VER=`mamonsu --version`
IFS=' ' read -ra MAMONSU_VERSION_ARRAY <<<$MAMONSU_FULL_VER
export MAMONSU_VERSION=${MAMONSU_VERSION_ARRAY[1]}

export PGSUPERUSER=postgres
export PSQL="psql -U $PGSUPERUSER"
WHOAMI=`whoami`
if [[ "$WHOAMI" != "postgres" ]]
then
  $PSQL -U postgres -c "CREATE USER $WHOAMI SUPERUSER" | true
  $PSQL -U postgres -c "CREATE DATABASE $WHOAMI OWNER $WHOAMI" | true
  export PGSUPERUSER=$WHOAMI
  export PSQL="psql -U $PGSUPERUSER"
fi
echo "PGSUPERUSER=$PGSUPERUSER"
echo "PSQL=$PSQL"

function check_db_objects() {
  echo "-------- check mamonsu schema all tables and functions"
  MAMONSU_USER=$1
  MAMONSU_DB=$2
  PG_SERVER_VERSION=`$PSQL $DB -c "SHOW server_version_num" -t -A`
  WALXLOG=nodata
  if [[ $PG_SERVER_VERSION -ge "100000" ]]
  then
    WALXLOG=wal
  else
    WALXLOG=xlog
  fi

  if [[ $MAMONSU_DB ]]
  then
    DB="-d $MAMONSU_DB"
    MAMONSU_DB=$MAMONSU_DB
  else
    DB=""
    MAMONSU_DB=$PGSUPERUSER
  fi
  echo "MAMONSU_USER = $MAMONSU_USER, MAMONSU_DB = $MAMONSU_DB"

  $PSQL $DB -c "\dt mamonsu.config" | grep "mamonsu.*config.*table.*$MAMONSU_USER"  || exit 11
  MAMONSU_TIMESTAMP_NAME=`echo $MAMONSU_VERSION | sed 's/\./\_/g'`
  $PSQL $DB -c "\dt mamonsu.timestamp_master_$MAMONSU_TIMESTAMP_NAME" | grep  "mamonsu.*timestamp_master_$MAMONSU_TIMESTAMP_NAME.*table.*$MAMONSU_USER"  || exit 11
  $PSQL $DB -c "\df mamonsu.timestamp_master_update" | grep  "mamonsu.*timestamp_master_update"  || exit 11
  $PSQL $DB -c "\df mamonsu.timestamp_get" | grep  "mamonsu.*timestamp_get"  || exit 11
  $PSQL $DB -c "\df mamonsu.count_autovacuum" | grep  "mamonsu.*count_autovacuum"  || exit 11
  $PSQL $DB -c "\df mamonsu.get_oldest_xid" | grep  "mamonsu.*get_oldest_xid"  || exit 11
  $PSQL $DB -c "\df mamonsu.get_oldest_transaction" | grep  "mamonsu.*get_oldest_transaction"  || exit 11
  echo "WALXLOG $WALXLOG"
  $PSQL $DB -c "\df mamonsu.count_"$WALXLOG"_files" | grep  "mamonsu.*count_"$WALXLOG"_files"  || exit 11
  $PSQL $DB -c "\df mamonsu.buffer_cache" | grep  "mamonsu.*buffer_cache"  || exit 11
  $PSQL $DB -c "\df mamonsu.archive_command_files" | grep  "mamonsu.*archive_command_files"  || exit 11
  $PSQL $DB -c "\df mamonsu.archive_stat" | grep  "mamonsu.*archive_stat"  || exit 11
  $PSQL $DB -c "\df mamonsu.get_sys_param" | grep  "mamonsu.*get_sys_param"  || exit 11
  $PSQL $DB -c "\df mamonsu.get_connections_states" | grep  "mamonsu.*get_connections_states"  || exit 11
  $PSQL $DB -c "\df mamonsu.prepared_transaction" | grep  "mamonsu.*prepared_transaction"  || exit 11
  $PSQL $DB -c "\df mamonsu.count_"$WALXLOG"_lag_lsn" | grep  "mamonsu.*count_"$WALXLOG"_lag_lsn"  || exit 11
}

function pg_drop_database() {
  DB=$1
  echo "-------- drop $DB"
  $PSQL -c "SELECT pg_cancel_backend(pid) FROM pg_stat_activity WHERE datname = '$DB'"
  $PSQL -c "DROP DATABASE IF EXISTS $DB"
}

function pg_drop_user() {
  PG_USER=$1
  echo "-------- drop $PG_USER"
  USER_EXISTS=`$PSQL -c "SELECT 1 FROM pg_user WHERE usename = '$PG_USER'"  -t -A`
  if [[ $USER_EXISTS ]]
  then
    DBS=`psql -c "SELECT datname FROM pg_database WHERE datname NOT IN ('template0','template1')" -t -A`

    for DB in $DBS
    do
      $PSQL -d $DB -c "REASSIGN OWNED BY $PG_USER TO $PGSUPERUSER"
      $PSQL -d $DB -c "DROP OWNED BY $PG_USER"
    done

    $PSQL -c "DROP USER $PG_USER"
  else
      echo "user $PG_USER does not exist"
  fi
}

echo && echo "------> mamonsu bootstrap -x -U postgres -d mamonsu_test_db"
# prepare
pg_drop_user mamonsu
# test
mamonsu bootstrap -x -U postgres -d mamonsu_test_db
# check
check_db_objects mamonsu mamonsu_test_db


echo && echo "------> mamonsu bootstrap -x -U postgres -d test_db"
# prepare
pg_drop_user mamonsu
pg_drop_database test_db
$PSQL -c "CREATE DATABASE test_db"
# test
mamonsu bootstrap -x -U postgres -d test_db
# check
check_db_objects mamonsu test_db

echo && echo "------> mamonsu bootstrap -x -U test_superuser -d test_superuser"
# prepare
pg_drop_user mamonsu
pg_drop_database test_db
pg_drop_user test_superuser
pg_drop_database test_superuser
$PSQL -c "CREATE USER test_superuser SUPERUSER"
$PSQL -c "CREATE DATABASE test_superuser OWNER test_superuser"
# test
mamonsu bootstrap -x -U test_superuser -d test_superuser
# check
check_db_objects mamonsu test_superuser

echo && echo "------>mamonsu bootstrap -x -U test_superuser -d test_superuser -h localhost -p 5432"
# prepare
pg_drop_user mamonsu
pg_drop_user test_superuser
pg_drop_database test_superuser
$PSQL -c "CREATE USER test_superuser SUPERUSER"
$PSQL -c "CREATE DATABASE test_superuser OWNER test_superuser"
# test
mamonsu bootstrap -x -U test_superuser -d test_superuser -h localhost -p 5432
# check
check_db_objects mamonsu test_superuser
# drop
pg_drop_user mamonsu
pg_drop_user test_superuser
pg_drop_database test_superuser

# bootstrap for other tests
mamonsu bootstrap -x -U postgres -d mamonsu_test_db

exit 0
