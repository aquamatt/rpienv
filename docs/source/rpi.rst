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
