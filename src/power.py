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
from data_logger import DataLogger
import settings


# board pin mapping
INPUT_PIN = 18
LED_DETECT = 12
LED_READY = 16


DATA_LOGGER = DataLogger()


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
        DATA_LOGGER.put(power, now)

        FlashAction().start()

    def setup(self):
        print("Setting up the board")
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(INPUT_PIN, GPIO.IN)
        GPIO.setup(LED_DETECT, GPIO.OUT)
        GPIO.setup(LED_READY, GPIO.OUT)

        GPIO.add_event_detect(
            INPUT_PIN, GPIO.FALLING,
            callback=self.process, bouncetime=100)
        print("Monitoring started")


def run_monitor():
    # Daemon is killed with a SIGTERM, as might happen from CLI by a user with
    # kill, so we trap and ensure a clean shutdown if this happens.
    signal.signal(signal.SIGTERM, shutdown)
    FlashReady().start()
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
    DATA_LOGGER.stop()
    GPIO.cleanup()
    sys.exit()


def startup():
    DATA_LOGGER.init(settings.LOGGERS)
    DATA_LOGGER.start()
    FlashMonitor().setup()
    run_monitor()


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
