#!/usr/bin/env python
#
# Hacked utility - not polished end-user code. This is left in the repository
# to provide examples only.
#
# This is used to copy data from one Influx DB to another. It's not the best
# way, but it worked nicely for my needs.

import sys

from influxdb import InfluxDBClient

import settings


SOURCE = InfluxDBClient(**settings.INFLUXDB_HOSTED)
DEST = InfluxDBClient(**settings.INFLUXDB_DO)

BLOCK_SIZE = 100


def point(time, power):
    json_point = {
        "measurement": 'electricity_power',
        "fields": {"power": power},
        "tags": {},
        "time": time
        }
    return json_point


def copy():
    results = SOURCE.query(
        "select * from electricity_power where time > now() - 4h")
    json_data = []
    for record in results['electricity_power']:
        json_data.append(point(**record))

        if len(json_data) == BLOCK_SIZE:
            DEST.write_points(json_data)
            json_data = []
            sys.stdout.write(".")
            sys.stdout.flush()

    if json_data:
        DEST.write_points(json_data)
        json_data = []
        sys.stdout.write(".")
        sys.stdout.flush()


if __name__ == '__main__':
    copy()
