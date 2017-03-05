#!/bin/bash
#
# install an init script
#
# Use:
#
# $ ./install_init_script.sh <power|ptrh>

PROG=$1

if [ "${PROG}" == "" ]
then
    echo "You must specify one of <power|ptrh> to install"
    exit 1
fi

sudo apt-get install -y chkconfig
sudo cp ${PROG}.init.d /etc/init.d/${PROG}
sudo chmod +x /etc/init.d/${PROG}
sudo chkconfig -a ${PROG}

echo ${PROG} init script installed
echo Ensure that /usr/local/rpienv is the virtualenv root
echo and that /usr/local/rpienv/rpienv contains ${PROG}.py
