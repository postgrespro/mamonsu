#!/usr/bin/env bash

# Copyright Notice:
# © (C) Postgres Professional 2015-2016 http://www.postgrespro.ru/
# Distributed under Apache License 2.0
# Распространяется по лицензии Apache 2.0

set -ex
set -o errexit
set -o pipefail

# fix https://github.com/moby/moby/issues/23137
ulimit -n 1024

yum install rpm-sign createrepo gnupg rsync expect rsync -y -q

export INPUT_DIR=/app/in
export OUT_DIR=/app/www

export repo_name=mamonsu
export KEYS_DIR=$OUT_DIR/$repo_name/keys

cd $INPUT_DIR
mkdir -p "$KEYS_DIR"
rsync /app/repo/gnupg/key.public $KEYS_DIR/GPG-KEY-MAMONSU
chmod 755 $KEYS_DIR
chmod +x /app/repo/autosign.sh
echo -e 'User-agent: *\nDisallow: /' > $OUT_DIR/$repo_name/robots.txt

cp -arv /app/repo/rpmmacros /root/.rpmmacros
cp -arv /app/repo/gnupg /root/.gnupg
chmod -R 0600 /root/.gnupg

cd $INPUT_DIR/$repo_name
for pkg_full_version in $(ls); do

#	[ ! -z "$CODENAME" ] && export DISTRIB_VERSION=$CODENAME
	RPM_DIR=$OUT_DIR/$repo_name/$pkg_full_version/rpm/${DISTRIB}-${CODENAME}
	mkdir -p "$RPM_DIR"

	cp -arv $INPUT_DIR/$repo_name/$pkg_full_version/* $RPM_DIR/

	for f in $(ls $RPM_DIR/*.rpm); do rpm --addsign $f || exit 1; done
	createrepo $RPM_DIR/
done

rm -rf /root/.rpmmacros
rm -rf /root/.gnupg
