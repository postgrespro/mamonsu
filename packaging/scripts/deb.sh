#!/usr/bin/env bash

set -exu
set -o errexit
set -o pipefail
ulimit -n 1024

export DEBIAN_FRONTEND=noninteractive
echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

apt-get -qq update

cp -a /app/in /var/build
find /var/build -type d -exec chmod 0755 {} \;
find /var/build -type f -exec chmod 0644 {} \;

#apt-get update -m || apt-get update -m || apt-get update -m
apt-get install -qq make dpkg-dev debhelper python-dev python-setuptools > /dev/null

cd /var/build
make deb

#mkdir -p /app/in/build/out/${DISTRIB}/${DISTRIB_VERSION}
cp *.deb /app/out
