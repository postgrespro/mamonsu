#!/bin/sh

# mamonsu metrics tests

# default parameters:
PG_VERSION="14"

for i in "$@"
do
case $i in
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
echo "---> Test MAMONSU metrics"
echo

while read metric; do
    GREP=$( mamonsu agent metric-get ${metric} | grep "pgsql\|sys\|mamonsu" )
    if [ -z "$GREP" ]; then
	      echo "---> ERROR: Cannot found metric $metric"
#        exit 11
    fi
done </mamonsu/github-actions-tests/sources/metrics-linux-${PG_VERSION}.txt

echo && echo
