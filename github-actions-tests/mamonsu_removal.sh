#!/bin/sh

# default parameters:
OS="centos:7"

for i in "$@"
do
case $i in
    --os=*)
    OS="${i#*=}"
    shift
    ;;
    *)
          # unknown option
    ;;
esac
done

echo && echo
echo "================================================================================================================="
echo "---> Remove mamonsu"
echo && echo

if [ "${OS%:*}" = "centos" ]; then
  sudo yum erase mamonsu -y
  echo "---> mamonsu directories and files after removal:"
  sudo find / -name "mamonsu" 2>/dev/null
elif [ "${OS%:*}" = "ubuntu" ]; then
  sudo apt-get purge mamonsu -y
  echo "---> mamonsu directories and files after removal:"
  sudo find / -name "mamonsu" 2>/dev/null
fi