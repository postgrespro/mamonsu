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
echo "---> Install Mamonsu latest"
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
    sudo mkdir -p /var/log/mamonsu
    sudo touch /var/log/mamonsu/mamonsu.log
    chmod -R 777 /var/log/mamonsu/
    sudo mkdir -p /etc/mamonsu
    sudo touch /etc/mamonsu/agent.conf
    cat /mamonsu/github-actions-tests/sources/agent_3.3.1.conf > /etc/mamonsu/agent.conf
    chmod -R 777 /etc/mamonsu/
    sudo yum -y install ./mamonsu*.rpm
    systemctl daemon-reload
    systemctl restart mamonsu
    sleep 5
    echo && echo && echo "Mamonsu version:"
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
    sudo mkdir -p /var/log/mamonsu
    sudo touch /var/log/mamonsu/mamonsu.log
    chmod -R 777 /var/log/mamonsu/
    sudo mkdir -p /etc/mamonsu
    sudo touch /etc/mamonsu/agent.conf
    cat /mamonsu/github-actions-tests/sources/agent_3.3.1.conf > /etc/mamonsu/agent.conf
    chmod -R 777 /etc/mamonsu/
    sudo apt-get -y install ./mamonsu*.deb
    service mamonsu restart
    sleep 5
    echo && echo && echo "Mamonsu version:"
    mamonsu --version
    echo && echo

fi
