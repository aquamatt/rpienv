#!/bin/bash
#
# install the power monitor init script

sudo apt-get install -y chkconfig
sudo cp power.init.d /etc/init.d/power
sudo chmod +x /etc/init.d/power
sudo chkconfig -a power

echo Power monitor installed
echo Ensure that /usr/local/rpienv is the virtualenv root
echo and that /usr/local/rpienv/rpienv contains power.py
