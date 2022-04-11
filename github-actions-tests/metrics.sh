#!/bin/sh

# mamonsu metrics tests

# default parameters:
PG_VERSION="14"
OS="centos:7"

for i in "$@"
do
case $i in
    --os=*)
    OS="${i#*=}"
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

METRICS_FILE="/mamonsu/github-actions-tests/sources/metrics-linux-${PG_VERSION}.txt"

echo && echo
echo "================================================================================================================="
echo "---> Test MAMONSU metrics"
echo

# ======================================================================================================================
# some PG preparations

PG_PATH=""
if [ "${OS%:*}" = "centos" ]; then
    PACKAGE="postgresql${PG_VERSION//./}-server postgresql${PG_VERSION//./}-contrib"
    PG_PATH="/usr/pgsql-${PG_VERSION}/bin/"
elif [ "${OS%:*}" = "ubuntu" ]; then
    PACKAGE="postgresql-${PG_VERSION} postgresql-contrib-${PG_VERSION}"
    PG_PATH="/usr/lib/postgresql/${PG_VERSION}/bin/"
fi

# archive_mode preps
sudo -u postgres ${PG_PATH}psql -d mamonsu_test_db -c "DO
\$do\$
DECLARE
   func_name varchar;
BEGIN
   SELECT proname INTO func_name FROM pg_proc WHERE proname LIKE 'pg_switch_%';
   EXECUTE FORMAT('SELECT %s();', func_name);
END
\$do\$;"

# pg_stat_statements preps
sudo -u postgres ${PG_PATH}psql -d mamonsu_test_db -c "CREATE EXTENSION pg_stat_statements;"

# wait few intervals to get all possible metrics
sleep 200

# read metric for specific version
while read metric; do
    GREP=$( mamonsu agent metric-get ${metric} | grep "pgsql\|sys\|mamonsu" )
    if [ -z "$GREP" ]; then
	      echo "---> ERROR: Cannot found metric $metric"
        exit 11
    fi
done <"${METRICS_FILE}"

echo && echo
