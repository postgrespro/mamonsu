#!/usr/bin/expect -f

# Copyright Notice:
# © (C) Postgres Professional 2015-2016 http://www.postgrespro.ru/
# Distributed under Apache License 2.0
# Распространяется по лицензии Apache 2.0

set rpmfile [lindex $argv 0]
spawn rpm --addsign $rpmfile
expect "Enter pass phrase:"
send -- "\r"
expect eof
