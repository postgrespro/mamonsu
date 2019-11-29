#!/usr/bin/env bash

# Copyright Notice:
# © (C) Postgres Professional 2015-2016 http://www.postgrespro.ru/
# Distributed under Apache License 2.0
# Распространяется по лицензии Apache 2.0

set -exu
set -o errexit
set -o pipefail

# fix https://github.com/moby/moby/issues/23137
ulimit -n 1024

export INPUT_DIR=/app/in # dir with builded deb
export repo_name=mamonsu
export OUT_DIR=/app/www/$repo_name
#export DEB_DIR=$OUT_DIR/deb
export KEYS_DIR=$OUT_DIR/keys
export CONF=/app/repo/conf

export DEBIAN_FRONTEND=noninteractive
echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

apt-get -qq update
apt-get -qq install reprepro gnupg rsync expect rsync dpkg-dev

mkdir -p $KEYS_DIR
#mkdir -p $DEB_DIR

cp -av /app/repo/gnupg /root/.gnupg
rsync /app/repo/gnupg/key.public $KEYS_DIR/GPG-KEY-MAMONSU
echo -e 'User-agent: *\nDisallow: /' > $OUT_DIR/robots.txt

cd $INPUT_DIR/$repo_name
for pkg_full_version in $(ls); do

	DEB_DIR=$OUT_DIR/$pkg_full_version/deb

	mkdir -p $DEB_DIR
	cd $DEB_DIR
	cp -av $CONF ./

	# make remove-debpkg tool
	#echo -n "#!"        > remove-debpkg
	#echo "/bin/sh"      >> remove-debpkg
	#echo "CODENAME=\$1" >> remove-debpkg
	#echo "DEBFILE=\$2"  >> remove-debpkg
	#echo "DEBNAME=\`basename \$DEBFILE | sed -e 's/_.*//g'\`"   >> remove-debpkg
	#echo "reprepro --waitforlock 5 remove \$CODENAME \$DEBNAME" >> remove-debpkg
	#chmod +x remove-debpkg

	#find $INPUT_DIR/ -name '*.changes' -exec reprepro -P optional -Vb . include ${CODENAME} {} \;
	# find $INPUT_DIR/$repo_name -name "*${CODENAME}*.deb" -exec ./remove-debpkg $CODENAME {} \;
	# find $INPUT_DIR/$repo_name -name "*${CODENAME}*.dsc" -exec reprepro --waitforlock 5 -i undefinedtarget --ignore=missingfile -P optional -S main -Vb . includedsc $CODENAME {} \;
	find $INPUT_DIR/$repo_name -name "*.deb" -exec reprepro --waitforlock 5 -i undefinedtarget --ignore=missingfile -P optional -Vb . includedeb $CODENAME {} \;
	reprepro export $CODENAME

	rm -f remove-debpkg
	rm -rf ./conf
	rm -rf /root/.gnupg
done
