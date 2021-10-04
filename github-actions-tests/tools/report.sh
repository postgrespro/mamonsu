#!/bin/sh

# 'mamonsu report' tool testing

echo && echo
echo "================================================================================================================="
echo "---> Test MAMONSU REPORT tool"
echo && echo

echo && echo "------> mamonsu report"
mamonsu report
echo && echo "------> mamonsu report --port 5433"
mamonsu report --port 5433
echo && echo "------> mamonsu report --run-system=false"
mamonsu report --run-system=false
echo && echo "------> mamonsu report --run-postgres=false"
mamonsu report --run-postgres=false
echo && echo "------> mamonsu report --disable-sudo"
mamonsu report --disable-sudo
echo && echo "------> mamonsu report -w rep1.txt"
mamonsu report -w rep1.txt
echo && echo "------> mamonsu report --report-path=rep2.txt"
mamonsu report --report-path=rep2.txt

exit 0
