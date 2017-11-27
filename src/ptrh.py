#!/usr/bin/env python
#
# Monitor atmostpheric pressure, temperature and relative humidity.
#
# use:
# $ ptrh.py
#
from __future__ import division
import math
import os
import sys
import signal
import threading
import time

import Adafruit_BMP.BMP085 as BMP085
import Adafruit_DHT as DHT
import RPi.GPIO as GPIO
import optfn

import dallas
from daemon import Daemon
from data_logger import DataLogger
import settings


DATA_LOGGER = DataLogger()
INDICATOR_LED = getattr(settings, "INDICATOR_LED", None)

MEASURE_PRESSURE = getattr(settings, "MEASURE_PRESSURE", True)
MEASURE_RH = getattr(settings, "MEASURE_RH", True)
MEASURE_WLAN = getattr(settings, "MEASURE_WLAN", False)
WLAN_INTERFACE = getattr(settings, "WLAN_INTERFACE", "wlan0")


class FlashIndicator(threading.Thread):
    """
    Flash the indicator LED
    """
    def run(self):
        GPIO.output(INDICATOR_LED, 1)
        time.sleep(0.02)
        GPIO.output(INDICATOR_LED, 0)


def _init_bmp180():
    mode_string = getattr(settings, "BMP180", "HIGHRES")
    if mode_string not in ["ULTRAHIGHRES", "HIGHRES", "STANDARD"]:
        raise Exception("Invalid BMP180 resolution mode: {}"
                        .format(mode_string))
    mode = getattr(BMP085, "BMP085_{}".format(mode_string))
    bmp_sensor = BMP085.BMP085(mode=mode)
    return bmp_sensor


def _read_bmp180(bmp_sensor):
    temp = bmp_sensor.read_temperature()
    pressure = bmp_sensor.read_sealevel_pressure(
        altitude_m=settings.BMP180_ELEVATION)
    return temp, pressure


def _init_dht():
    rh_sensor_name = getattr(settings, "RH_DEVICE", "DHT22")
    if rh_sensor_name not in ["DHT11", "DHT22", "AM2302"]:
        raise Exception("Invalid relative humidity sensor: {}"
                        .format(rh_sensor_name))
    rh_sensor = getattr(DHT, rh_sensor_name)
    rh_pin = getattr(settings, "RH_PIN")
    return rh_sensor, rh_pin


def _read_dht(rh_sensor, rh_pin):
    # Try to grab a sensor reading.  Use the read_retry method which
    # will retry up to 15 times to get a sensor reading (waiting
    # 2 seconds between each retry).
    humidity, dht_temp = DHT.read_retry(rh_sensor, rh_pin)
    return humidity, dht_temp


def read_wlan_stats():
    """
    Return WLAN quality and strength
    """

    with os.popen("iwconfig {}".format(WLAN_INTERFACE), "r") as f:
        for l in f:
            if "Quality" in l:
                [_, quality, _, strength, _] = l.split()
                try:
                    quality = 100.0 * eval(quality.split("=")[1])
                except Exception:
                    quality = -1.0
                strength = float(strength.split("=")[1])
                break
    return quality, strength


def dew_point(temp, rh):
    """
    Approximate dew-point calculation with Magnus formula as per:
    https://en.wikipedia.org/wiki/Dew_point
    """
    b = 18.678
    c = 257.14

    # NOAA constants
    # b = 17.67
    # c = 243.5
    gamma = math.log(rh/100.0) + (b*temp)/(c+temp)
    t_dp = (c*gamma) / (b-gamma)
    return t_dp


def run_monitor():
    # Daemon is killed with a SIGTERM, as might happen from CLI by a user with
    # kill, so we trap and ensure a clean shutdown if this happens.
    signal.signal(signal.SIGTERM, shutdown)

    # setup the BMP180 library (atmospheric pressure)
    if MEASURE_PRESSURE:
        bmp_sensor = _init_bmp180()

    # setup the DHT22 library (relative humidity)
    if MEASURE_RH:
        rh_sensor, rh_pin = _init_dht()

    # enter measurement loop
    try:
        while True:
            now = time.time()

            fields = []

            # BMP180
            if MEASURE_PRESSURE:
                temp, pressure = _read_bmp180(bmp_sensor)
                fields.extend([
                    ("temp_bmp180", temp),
                    ("pressure", pressure/100.0),
                    ])

            # DHT22
            if MEASURE_RH:
                humidity, dht_temp = _read_dht(rh_sensor, rh_pin)

                # Note that sometimes you won't get a reading from DHT22 and
                # the results will be null (because Linux can't
                # guarantee the timing of calls to read the sensor).
                if humidity is not None:
                    fields.append(("rh", humidity))
                if dht_temp is not None:
                    fields.append(("temp_dht22", dht_temp))

                if (humidity is not None) and (dht_temp is not None):
                    fields.append(("dew_point", dew_point(dht_temp, humidity)))

            # DS18B20
            # Measure temperature from each of the sensors configured
            for id, location in settings.DALLAS_TEMP_DEVICES:
                temp = dallas.read_temperature(id)
                if temp is not None:
                    fields.append(("temp_{}".format(location), temp))

            measured = time.time()

            DATA_LOGGER.put("environment", fields, now)

            # monitor how long this loop is taking to execute
            sent = time.time()
            DATA_LOGGER.put("measure_loop",
                            [("measurements", measured-now),
                             ("transmit", sent-measured)], now)

            # WiFi
            if MEASURE_WLAN:
                _, strength = read_wlan_stats()
                DATA_LOGGER.put("system_stats",
                                [("wlan_strength", strength)], now)

            if INDICATOR_LED is not None:
                FlashIndicator().start()

            time.sleep(settings.PRESSURE_MONITOR_INTERVAL)
    except KeyboardInterrupt:
        print("Manual quit")
    except Exception, ex:
        print("An error occurred: {}".format(ex.message))
    finally:
        shutdown()


def shutdown(*args, **kwargs):
    print("Closing loggers and exiting")
    DATA_LOGGER.stop()
    GPIO.cleanup()
    sys.exit()


def startup():
    DATA_LOGGER.init(settings.LOGGERS)
    DATA_LOGGER.start()

    if INDICATOR_LED is not None:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(INDICATOR_LED, GPIO.OUT)
    run_monitor()


class PTRHDaemon(Daemon):
    def run(self):
        startup()


def daemonise(pidfile="/var/run/ptrh.pid", kill=False, restart=False):
    daemon = PTRHDaemon(
        pidfile=pidfile,
        stdout="/tmp/ptrh.out",
        stderr="/tmp/ptrh.err"
        )
    if restart:
        daemon.restart()
    elif kill:
        daemon.stop()
    else:
        daemon.start()


def cli_handler(pidfile='/var/run/ptrh.pid', kill=False, restart=False,
                nodaemon=False):
    """
    Use:

    > ./ptrh.py [options]

    --pidfile=<pid file path>  - default /var/run/ptrh.pid
    --kill                     - kill running daemon
    --restart                  - restart daemon
    --nodaemon                 - default is False (daemonise)

    Output is sent to /tmp/ptrh.[out|err]
    """
    if nodaemon:
        startup()
    else:
        daemonise(pidfile, kill, restart)


if __name__ == '__main__':
    optfn.run(cli_handler)
