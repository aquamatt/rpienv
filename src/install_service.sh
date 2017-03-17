#!/bin/bash
#
# install a systemd service
#
# Use:
#
# $ ./install_service.sh <power|ptrh>
PROG=$1

if [ "${PROG}" == "" ]
then
    echo "You must specify one of <power|ptrh> to install"
    exit 1
fi

SERVICE=${PROG}.service
SERVICE_FILE=/etc/systemd/system/${SERVICE}
sudo cp ${SERVICE} ${SERVICE_FILE}
sudo chown root:root ${SERVICE_FILE}
sudo chmod 0644 ${SERVICE_FILE}

sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE}
sudo systemctl start ${SERVICE}
sleep 2
sudo systemctl status ${SERVICE}

echo ${PROG} service installed
echo Ensure that /usr/local/rpienv is the virtualenv root
echo and that /usr/local/rpienv/rpienv contains ${PROG}.py
