#!/usr/bin/env python
"""
Monitors and publishes network speed test results (from speedtest.net)

As we are settled on using SystemD we are not providing daemon options any
more.
"""
import optfn
import os
import signal
import sys
import time

from data_logger import DataLogger
import settings

DATA_LOGGER = DataLogger()
BITS_IN_MEGABIT = 1024 * 1024
NET_SPEED_TEST_INTERVAL = getattr(settings, "NET_SPEED_TEST_INTERVAL", 300)
SPEEDTEST_BIN = getattr(settings, "SPEEDTEST_BIN", "speedtest-cli")


def run_monitor(debug):
    # Daemon is killed with a SIGTERM, as might happen from CLI by a user with
    # kill, so we trap and ensure a clean shutdown if this happens.
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            with os.popen("{} --csv".format(SPEEDTEST_BIN), "r") as f:
                results = f.next().strip().split(',')[-3:]

            ping, download, upload = [float(x) for x in results]
            download = download / BITS_IN_MEGABIT
            upload = upload / BITS_IN_MEGABIT

            if debug:
                print("Response from speedtest: {}".format(results))
                print("ping/down/up: {} ms / {} Mbit/s / {} Mbit/s"
                      .format(ping, download, upload))
            else:
                now = time.time()
                DATA_LOGGER.put("broadband",
                                [("ping", ping),
                                 ("download", download),
                                 ("upload", upload)], now)

            time.sleep(NET_SPEED_TEST_INTERVAL)

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


def startup(debug):
    DATA_LOGGER.init(settings.LOGGERS)
    DATA_LOGGER.start()

    run_monitor(debug)


def cli_handler(debug=False):
    """
    Use:

       $ netmon.py [--debug]

    The debug option causes output to go to stdout instead of other loggers.
    """
    startup(debug)


if __name__ == '__main__':
    optfn.run(cli_handler)



