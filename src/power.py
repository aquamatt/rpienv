#!/usr/bin/env python
#
# Power monitor uses TEPT5700 phototransistor to sense flashing of the
# metrology LED on a modern electricity meter. The timing between flashes
# corresponds to 1Wh of electricity consumed (the manual talks of 1000 impulses
# per kWh).
#
# use:
# $ power.py [options]
#
# Options:
#
#  -N               no-daemonise. By default the tracker will daemonise.
#  -l  <logfile>    defaults to /tmp/power_<time>

from optparse import OptionParser
import sys
import threading
import time

import RPi.GPIO as GPIO


# board pin mapping
INPUT_PIN  = 18
LED_DETECT = 12
LED_READY  = 16

DATA_FILE = "/tmp/power_{}.txt".format(int(time.time())-1422000000)


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


def process(self):
    sys.stdout.write(".")
    sys.stdout.flush()
    with open(DATA_FILE, "at") as df:
        df.write("{}\n".format(time.time()))
    FlashAction().start()


def setup():
    print("Setting up the board")
    print("Output will go to {}".format(DATA_FILE))
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(INPUT_PIN, GPIO.IN)
    GPIO.setup(LED_DETECT, GPIO.OUT)
    GPIO.setup(LED_READY, GPIO.OUT)

    GPIO.add_event_detect(INPUT_PIN, GPIO.FALLING, callback=process, bouncetime=200)


def run():
    FlashReady().start()
    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        print("Manual quit")
    except Exception, ex:
        print("An error occurred: {}".format(ex.message))
    finally:
        print("CLEANING UP GPIO")
        GPIO.cleanup()


if __name__=='__main__':
    parser = OptionParser(usage=__doc__)
    parser.add_option("-N", "--no-daemonise", dest="nodaemonise",
                      default=False, action="store_true",
                      help="Prevent monitor from daemonising")
    parser.add_option("-l", "--log", dest="log_file",
                      help="Set log file destination")
    (options, args) = parser.parse_args()

    setup()
    run()
