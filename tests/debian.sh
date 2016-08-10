#/bin/sh -ex

# test build
cd /var/tmp && (apt-get update || apt-get update || apt-get update)
(apt-get install -y make dpkg-dev debhelper python-dev python-setuptools || apt-get install -y make dpkg-dev debhelper python-dev python-setuptools)
make deb && dpkg -i mamonsu*.deb && cd /

# test alive after 5 sec
/etc/init.d/mamonsu restart
sleep 5 && /etc/init.d/mamonsu stop

# test uninstall
apt-get purge -y mamonsu
