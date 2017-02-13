Raspberry Pi notes
******************

General
=======

Pinout map: https://pinout.xyz/


Configuration
=============

Wifi
----

To connect to WiFi, edit `/etc/wpa_supplicant/wpa_supplicant.conf` and append:

.. code-block:: text

    network={
      ssid="<YOUR SID>"
      psk="<YOUR KEY>"
    }

No more needs to be done.

General setup
-------------

If you use `raspi-config` to configure the host you can set whether it logs in
on boot or not, starts X-Windows or not and many other things. You can also set
its hostname which, thanks to Bonjour protocol, means you can ssh to
`<hostname>.local` from another machine on the same network and connect without
knowing the IP address.

By default, the SSH server is disabled. You can use `raspi-config` to enable or
the usual Debian systemd tools.

If you haven't set a hostname, or don't know it, NMap can help you find your
Pi:

.. code-block:: bash

    $ nmap -sP 192.168.2.0/24


Amend the network address and mask accordingly, of course.

WiFi modules
------------
We have discovered that not all USB WiFi modules are born equal. Whilst
generally suffering from weak reception, their small size and small antennas
make this inevitable. Careful positioning and orientation can make a big
difference to signal strength (you can see current signal strength with
`iwconfig <network device>`) and it is always worth experimenting with the
orientation of your device to achieve better reception.

There is also considerable variation between WiFi modules. Of those that we
have tried, all have had a Ralink RT5370 module
(with the RT2800 kernel modules). Some had great signal strength, others not so
good, so it's likely internal construction that matters. Experimentation is
necessary.

WiFi power management
---------------------

A constant source of issues is WiFi on the Rasbian distribution. WiFi cutting
out, arbitrarily disconnecting etc. It seems this is related to power
management. Disable power management in `/etc/network/interfaces` by amending
the `wlan0` clause to add a `post-up` command as follows:

.. code-block:: bash

    allow-hotplug wlan0
    iface wlan0 inet manual
        wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
        post-up iwconfig wlan0 power off

.. note:: This has not been confirmed as a final solution as yet


Python environments
-------------------

The `RPi.GPIO` package is probably installed in the base distribution. If not,
and if you're on a Debian distro:

.. code-block:: bash

    $ sudo apt-get install rpi.gpio

Virtalenv environments are always useful. The default is not to include system
packages in a virtualenv, but that is awkward on the Pi as you'll likely want
RPi.GPIO, so the easiest is to create a virtualenv with:


.. code-block:: bash

    $ virtualenv <env dir> --system-site-packages

(don't forget to install `python-virtualenv` on the system for this)
