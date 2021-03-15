#!/bin/bash -ex

# тест команд mamonsu bootstrap *

# Требования:
# запуск psql от пользователя postgres psql -U postgres
# в pg_hba долвны быть разрешения для всех пользователей trust

MAMONSU_FULL_VER=`mamonsu --version`
IFS=' ' read -ra MAMONSU_VERSION_ARRAY <<<$MAMONSU_FULL_VER
export MAMONSU_VERSION=${MAMONSU_VERSION_ARRAY[1]}

export PGSUPERUSER=postgres
export PSQL="psql -U $PGSUPERUSER"
WHOAMI=`whoami`
if [[ "$WHOAMI" != "postgres" ]]
then
  $PSQL -U postgres -c "create user $WHOAMI superuser" | true
  $PSQL -U postgres -c "create database $WHOAMI owner $WHOAMI" | true
  export PGSUPERUSER=$WHOAMI
  export PSQL="psql -U $PGSUPERUSER"
fi
echo "PGSUPERUSER=$PGSUPERUSER"
echo "PSQL=$PSQL"

function check_db_objects() {
  MAMONSU_USER=$1
  MAMONSU_DB=$2
  PG_SERVER_VERSION=`$PSQL $DB -c "show server_version_num" -t -A`
  WALXLOG=nodata
  if [[ $PG_SERVER_VERSION -lt "100000" ]]
  then
    WALXLOG=xlog
  fi
  if [[ $PG_SERVER_VERSION -gt "100000" ]]
  then
    WALXLOG=wal
  fi

  if [[ $MAMONSU_DB ]]
  then
    DB="-d $MAMONSU_DB"
    MAMONSU_DB=$MAMONSU_DB
  else
    DB=""
    MAMONSU_DB=$PGSUPERUSER
  fi
  echo "MAMONSU_USER = $MAMONSU_USER, MAMONSU_DB = $MAMONSU_DB, DB= $DB"

  $PSQL $DB -c "\dt mamonsu_config" | grep  "mamonsu_config.*table.*$MAMONSU_USER"  || exit 11
  MAMONSU_TIMESTAMP_NAME=`echo $MAMONSU_VERSION | sed 's/\./\_/g'`
  $PSQL $DB -c "\dt mamonsu_timestamp_master_$MAMONSU_TIMESTAMP_NAME" | grep  "mamonsu_timestamp_master_$MAMONSU_TIMESTAMP_NAME.*table.*$MAMONSU_USER"  || exit 11
  $PSQL $DB -c "\df mamonsu_timestamp_master_update" | grep  "mamonsu_timestamp_master_update"  || exit 11
  $PSQL $DB -c "\df mamonsu_timestamp_get" | grep  "mamonsu_timestamp_get"  || exit 11
  $PSQL $DB -c "\df mamonsu_count_autovacuum" | grep  "mamonsu_count_autovacuum"  || exit 11
  $PSQL $DB -c "\df mamonsu_get_oldest_xid" | grep  "mamonsu_get_oldest_xid"  || exit 11
  $PSQL $DB -c "\df mamonsu_get_oldest_transaction" | grep  "mamonsu_get_oldest_transaction"  || exit 11
  echo "WALXLOG $WALXLOG"
  $PSQL $DB -c "\df mamonsu_count_"$WALXLOG"_files" | grep  "mamonsu_count_"$WALXLOG"_files"  || exit 11
  #$PSQL $DB -c "\df mamonsu_buffer_cache" | grep  "mamonsu_buffer_cache"  || exit 11
  $PSQL $DB -c "\df mamonsu_archive_command_files" | grep  "mamonsu_archive_command_files"  || exit 11
  $PSQL $DB -c "\df mamonsu_archive_stat" | grep  "mamonsu_archive_stat"  || exit 11
  $PSQL $DB -c "\df mamonsu_get_sys_param" | grep  "mamonsu_get_sys_param"  || exit 11
  $PSQL $DB -c "\df mamonsu_get_connections_states" | grep  "mamonsu_get_connections_states"  || exit 11
  $PSQL $DB -c "\df mamonsu_prepared_transaction" | grep  "mamonsu_prepared_transaction"  || exit 11
  $PSQL $DB -c "\df mamonsu_count_"$WALXLOG"_lag_lsn" | grep  "mamonsu_count_"$WALXLOG"_lag_lsn"  || exit 11
}

function pg_drop_database() {
  DB=$1
  $PSQL -c "select pg_cancel_backend(pid) from pg_stat_activity where datname = '$DB'"
  $PSQL -c "drop DATABASE if exists $DB"
}

function pg_drop_user() {
  PG_USER=$1

  USER_EXISTS=`$PSQL -c "select 1 from pg_user where usename = '$PG_USER'"  -t -A`
  if [[ $USER_EXISTS ]]
  then
    DBS=`psql -c "select datname from pg_database where datname not in ('template0','template1')" -t -A`

    for DB in $DBS
    do
      $PSQL -d $DB -c "REASSIGN OWNED BY $PG_USER TO $PGSUPERUSER"
      $PSQL -d $DB -c "DROP OWNED BY $PG_USER"
    done

    $PSQL -c "drop user  $PG_USER"
  else
      echo "user $PG_USER do not exists"
  fi
}

## test 1
echo test 1
### preparation
pg_drop_user mamonsu
$PSQL -c "create user mamonsu"

## test
mamonsu bootstrap -M mamonsu
##check
check_db_objects mamonsu


## test 2
echo test 2
### preparation
pg_drop_user mamonsu
pg_drop_database mamonsu
$PSQL -c "create user mamonsu"
$PSQL -c "create database mamonsu owner mamonsu"
## test
mamonsu bootstrap -M mamonsu -d mamonsu
check_db_objects mamonsu mamonsu

## test 3
echo test 3
pg_drop_user mamonsu
pg_drop_database mamonsu
pg_drop_user pgsuper_user
pg_drop_database pgsuper_user

$PSQL -c "create user mamonsu"
$PSQL -c "create database mamonsu"
$PSQL -c "create user pgsuper_user superuser"
$PSQL -c "create database pgsuper_user "

mamonsu bootstrap -M mamonsu  -U pgsuper_user

check_db_objects mamonsu pgsuper_user

## test 4
echo test 4
pg_drop_user mamonsu
pg_drop_database mamonsu
pg_drop_user pgsuper_user
pg_drop_database pgsuper_user

$PSQL -c "create user mamonsu"
$PSQL -c "create database mamonsu"
$PSQL -c "create user pgsuper_user superuser"
$PSQL -c "create database pgsuper_user "

mamonsu bootstrap -M mamonsu  -U pgsuper_user -h localhost -p 5432

check_db_objects mamonsu pgsuper_user

exit 0
