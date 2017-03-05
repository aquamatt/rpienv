#!/usr/bin/env python
#
# Monitor atmostpheric pressure, temperature and relative humidity.
#
# use:
# $ ptrh.py
#
from __future__ import division
import sys
import signal
import time

import Adafruit_BMP.BMP085 as BMP085
import Adafruit_DHT as DHT
import optfn

import dallas
from daemon import Daemon
from data_logger import DataLogger
import settings


DATA_LOGGER = DataLogger()

def run_monitor():
    # Daemon is killed with a SIGTERM, as might happen from CLI by a user with
    # kill, so we trap and ensure a clean shutdown if this happens.
    signal.signal(signal.SIGTERM, shutdown)

    # setup the BMP180 library (atmospheric pressure)
    mode_string = getattr(settings, "BMP180", "HIGHRES")
    if mode_string not in ["ULTRAHIGHRES", "HIGHRES", "STANDARD"]:
        raise Exception("Invalid BMP180 resolution mode: {}"
                        .format(mode_string))
    mode = getattr(BMP085, "BMP085_{}".format(mode_string))
    bmp_sensor = BMP085.BMP085(mode=mode)

    # setup the DHT22 library (relative humidity)
    rh_sensor_name = getattr(settings, "RH_DEVICE", "DHT22")
    if rh_sensor_name not in ["DHT11", "DHT22", "AM2302"]:
        raise Exception("Invalid relative humidity sensor: {}"
                        .format(rh_sensor_name))
    rh_sensor = getattr(DHT, rh_sensor_name)
    rh_pin = getattr(settings, "RH_PIN")

    # enter measurement loop
    try:
        while True:
            now = time.time()

            # BMP180
            temp = bmp_sensor.read_temperature()
            pres = bmp_sensor.read_sealevel_pressure(
                altitude_m=settings.BMP180_ELEVATION)

            # DHT22
            # Try to grab a sensor reading.  Use the read_retry method which
            # will retry up to 15 times to get a sensor reading (waiting
            # 2 seconds between each retry).
            humidity, dht_temp = DHT.read_retry(rh_sensor, rh_pin)

            # Post the response
            fields = [
                ("temp_bmp180", temp),
                ("pressure", pres/100.0),
                ]

            # Note that sometimes you won't get a reading from DHT22 and
            # the results will be null (because Linux can't
            # guarantee the timing of calls to read the sensor).
            if humidity is not None:
                fields.append(("rh", humidity))
            if dht_temp is not None:
                fields.append(("temp_dht22", dht_temp))

            # DS18B20
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
    sys.exit()


def startup():
    DATA_LOGGER.init(settings.LOGGERS)
    DATA_LOGGER.start()
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
