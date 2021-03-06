Home electrical power monitoring
********************************

Construction
============

Using the :ref:`ref-tept5700` biased by a 180kΩ resistor we detect
the metrology LED flash.

Voltage at collector is our input and is low when light present. The pull-up
resistor keeps the input stable. EMI cannot drop the voltage, so does not
generate spurious signals (as would be the case if R1 and D1 were swapped), but
it can overload the Pi input in extreme cases. The 1MΩ resistor R3 is intended
to limit current to the GPIO pin. It is sized as the largest to hand when the
author built this, but could probably be an order of magnitude larger.

.. image:: img/metrology_monitor.png

L1 and L2 are purely for the application to provide indication to the user.
One, for example, will flash each time the metrology LED flash is detected.

(diagram created with https://www.digikey.com/schemeit)

Monitor application
===================

A basic application for monitoring power consumption using the above described
hardware is included in this repository. `power.py` will report output to file,
to Librato and to InfluxDB.

Application installation
------------------------

Installation is somewhat manual for now.

* Copy the code to your RPi
* Create a virtual environment
* pip install `src/requirements.txt`

Before you can run the code, copy `settings.py.example` to `settings.py` and
put in appropriate keys, usernames and addresses.

Running the power monitor
-------------------------

The `power.py` script can be run standalone on the console as:

.. code-block:: bash

  > ./power.py --pidfile=/tmp/power.pid --nodaemon


But you will want to daemonise in time:

.. code-block:: bash

  > ./power.py --pidfile=/tmp/power.pid


To kill a daemon process:

.. code-block:: bash

  > ./power.py --pidfile=/tmp/power.pid --kill

To see options:

.. code-block:: bash

  > ./power.py --pidfile=/tmp/power.pid -h

Init script (systemD)
---------------------

systemd is the latest service management system being adopted by debian and is
present on recent Raspbian builds. It does a good job of re-starting processes
that die, and it simplifies programming because processes no longer need to
daemonise themselves and perform the double-fork dance.

A systemd service file is provided. To install:

* Symlink `/usr/local/rpienv` to the directory containing your virtualenv
* Symlink `/usr/local/rpienv/rpienv` to the `src` directory
* Run `install_service.sh` from the source code directory

The power monitor will now start on boot and can be managed with `systemctl`.

Init script (init.d - legacy)
-----------------------------

To keep the power tool running you need to install an init script:

* Symlink `/usr/local/rpienv` to the directory containing your virtualenv
* Symlink `/usr/local/rpienv/rpienv` to the `src` directory
* Run `install_init_script.sh` from the source code directory

The power monitor will now start on boot and can be managed with
`/etc/init.d/power`.


.. warning:: It is likely that we will remove the capability to daemonise the
             scripts in order to simplify them. Therefore initd will not be
             supported at that point.

Circuit board
=============

With some three-holes-per-strip strip board to hand we set about designing
a layout to move the circuit from breadboard to strip. We used DIY Layout
Creator, a Java program (hence Linux friendly) to design the layout. Obtain
from http://diy-fever.com/software/diylc/. The DIY source file is
:download:`here <img/monitor_circuit_board.diy>`.


.. image:: img/monitor_circuit_board.png
