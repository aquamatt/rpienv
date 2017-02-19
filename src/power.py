#!/usr/bin/env python
#
# Power monitor uses TEPT5700 phototransistor to sense flashing of the
# metrology LED on a modern electricity meter. The timing between flashes
# corresponds to 1Wh of electricity consumed (the manual talks of 1000 impulses
# per kWh).
#
# use:
# $ power.py
from __future__ import division
import sys
import signal
import threading
import time

import RPi.GPIO as GPIO
import optfn

from daemon import Daemon
from librato_logger import LibratoLogger
from influx_logger import InfluxLogger
from file_logger import FileLogger
import settings


# board pin mapping
INPUT_PIN = 18
LED_DETECT = 12
LED_READY = 16

DATA_FILE = "/tmp/power_{}.txt".format(int(time.time())-1422000000)

librato = LibratoLogger(name="power", settings=settings)
influxdb = InfluxLogger(name="electricity_power", settings=settings)
fileout = FileLogger(DATA_FILE)


class FlashAction(threading.Thread):
    def run(self):
        GPIO.output(LED_DETECT, 1)
        time.sleep(0.1)
        GPIO.output(LED_DETECT, 0)


class FlashReady(threading.Thread):
    def run(self):
        GPIO.output(LED_READY, 1)
        time.sleep(2)
        GPIO.output(LED_READY, 0)


class FlashMonitor(object):
    def __init__(self):
        self.last_time = 0

    def process(self, _):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        if now == dt:
            # this was first call, so quit as we have no delta
            return
#        1 Wh = 1J/s * 3600 Joules
#        energy used = 3600 Joules between flashes
#        power = 3600 / dt Joules/s
        power = 3600 / dt
        librato.put(power, now)
        fileout.put(power, now)
        influxdb.put(power, now)

        FlashAction().start()

    def setup(self):
        print("Setting up the board")
        print("Output will go to {}".format(DATA_FILE))
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(INPUT_PIN, GPIO.IN)
        GPIO.setup(LED_DETECT, GPIO.OUT)
        GPIO.setup(LED_READY, GPIO.OUT)

        GPIO.add_event_detect(
            INPUT_PIN, GPIO.FALLING,
            callback=self.process, bouncetime=200)


def run():
    # Daemon is killed with a SIGTERM, as might happen from CLI by a user with
    # kill, so we trap and ensure a clean shutdown if this happens.
    signal.signal(signal.SIGTERM, shutdown)
    FlashReady().start()
    librato.start()
    influxdb.start()
    fileout.start()
    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        print("Manual quit")
    except Exception, ex:
        print("An error occurred: {}".format(ex.message))
    finally:
        shutdown()


def shutdown(*args, **kwargs):
    print("CLEANING UP GPIO and loggers")
    librato.stop()
    influxdb.stop()
    fileout.stop()
    GPIO.cleanup()
    sys.exit()


def startup():
    FlashMonitor().setup()
    run()


class FlashMonitorDaemon(Daemon):
    def run(self):
        startup()


def daemonise(pidfile="/var/run/power.pid", kill=False, restart=False):
    daemon = FlashMonitorDaemon(
        pidfile=pidfile,
        stdout="/tmp/flashmonitor.out",
        stderr="/tmp/flashmonitor.err"
        )
    if restart:
        daemon.restart()
    elif kill:
        daemon.stop()
    else:
        daemon.start()


def cli_handler(pidfile='/var/run/power.pid', kill=False, restart=False,
                nodaemon=False):
    """
    Use:

    > ./power.py [options]

    --pidfile=<pid file path>  - default /var/run/power.pid
    --kill                     - kill running daemon
    --restart                  - restart daemon
    --nodaemon                 - default is False (daemonise)

    Output is sent to /tmp/flashmonitor.[out|err]
    """
    if nodaemon:
        startup()
    else:
        daemonise(pidfile, kill, restart)


if __name__ == '__main__':
    optfn.run(cli_handler)
