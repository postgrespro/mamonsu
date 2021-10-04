#!/bin/sh

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
done </mamonsu/github-actions-tests/sources/metrics-linux.txt

echo && echo
