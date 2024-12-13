#!/bin/sh

# default parameters:
OS="centos:7"
PG_VERSION="14"

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

echo && echo
echo "================================================================================================================="
echo "---> Install mamonsu latest"
echo && echo

# clean install mamonsu
if [ "${OS%:*}" = "centos" ]; then
    cd /mamonsu
    sudo yum install -y make
    sudo yum install -y rpm-build
    sudo yum install -y python3
    sudo yum install -y python3-devel

    sudo yum -y remove mamonsu
    make clean
    python3 setup.py clean --all
    rm -rf /etc/mamonsu; rm -rf /usr/bin/mamonsu; rm -rf /usr/local/bin/mamonsu; rm -rf /usr/lib/python3/dist-packages/mamonsu; rm -rf /usr/share/doc/mamonsu; rm -rf /usr/share/mamonsu; rm -rf /var/log/mamonsu; rm -rf /var/lib/mamonsu; rm -rf /run/mamonsu
    python3 setup.py build && python3 setup.py install
    make rpm
    sudo rpm -i ./mamonsu*.rpm
    cat /mamonsu/github-actions-tests/sources/agent_3.5.9.conf > /etc/mamonsu/agent.conf
    # ensuring mamonsu can actually start
    sudo su -s /bin/bash -c "mamonsu bootstrap -x --user postgres -d mamonsu_test_db" mamonsu
    /etc/init.d/mamonsu restart
    sleep 5
    echo && echo && echo "mamonsu version:"
    mamonsu --version
    echo && echo

elif [ "${OS%:*}" = "ubuntu" ]; then
    cd /mamonsu
    sudo apt-get install -y make
    sudo apt-get install -y python3-setuptools
    sudo apt-get install -y python3-dev
    sudo apt-get install -y dpkg-dev
    sudo apt-get install -y debhelper

    sudo apt-get -y remove mamonsu
    make clean
    python3 setup.py clean --all
    rm -rf /etc/mamonsu; rm -rf /usr/bin/mamonsu; rm -rf /usr/local/bin/mamonsu; rm -rf /usr/lib/python3/dist-packages/mamonsu; rm -rf /usr/share/doc/mamonsu; rm -rf /usr/share/mamonsu; rm -rf /var/log/mamonsu; rm -rf /var/lib/mamonsu; rm -rf /run/mamonsu
    python3 setup.py build && python3 setup.py install
    make deb
    sudo dpkg -i ./mamonsu*.deb
    cat /mamonsu/github-actions-tests/sources/agent_3.5.9.conf > /etc/mamonsu/agent.conf
    # ensuring mamonsu can actually start
    sudo su -s /bin/bash -c "mamonsu bootstrap -x --user postgres -d mamonsu_test_db" mamonsu
    service mamonsu restart
    sleep 5
    echo && echo && echo "mamonsu version:"
    mamonsu --version
    echo && echo

fi
