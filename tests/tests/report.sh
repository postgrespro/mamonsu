#!/bin/bash -ex


# тест команд mamonsu report *

# Требования:
# нет

mamonsu report
mamonsu report --port 5433
mamonsu report --run-system=false
mamonsu report --run-postgres=false
mamonsu report --disable-sudo
mamonsu report -w rep1.txt
mamonsu report --report-path=rep2.txt

