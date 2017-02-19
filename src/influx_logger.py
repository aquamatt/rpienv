"""
Data logger that sends data in batches to InfluxDB
"""
from datetime import datetime
import logging
import Queue
import sys
import threading
import time

from influxdb import InfluxDBClient

from data_logger import BaseLogger


logger = logging.getLogger("influx-logger")


class InfluxLoggerThread(threading.Thread):
    """
    Post data to Influx DB in batches
    """
    PERIOD = 5

    def __init__(self, data_queue, metric_name, settings):
        super(InfluxLoggerThread, self).__init__()
        self.data_queue = data_queue
        self.metric_name = metric_name
        self.influx = InfluxDBClient(**settings.INFLUXDB)

    def run(self):
        STOP = False
        json_data = []

        # keep looping until STOP is posted to the data_queue
        while True:
            time.sleep(InfluxLoggerThread.PERIOD)
            while True:
                try:
                    point = self.data_queue.get(block=False)
                    if point == "STOP":
                        STOP = True
                        break
                    timestamp, value = point
                    json_point = {
                         "measurement": self.metric_name,
                         "fields": {"power": value},
                         "tags": {},
                         "time": datetime.fromtimestamp(timestamp)
                        }
                    json_data.append(json_point)
                except Queue.Empty:
                    break
                except Exception as ex:
                    # ensure we don't crash out. Need to learn if anything
                    # else is to be done here.
                    sys.stderr.write("{}\n".format(ex.message))
                    sys.stderr.flush()

            if json_data:
                #  @todo WHAT OF NETWORK FAIL? DON'T CLEAR JSON SO TRY AGAIN
                #  @todo Be more specific about exceptions caught.
                try:
                    self.influx.write_points(json_data)
                except Exception as ex:
                    sys.stderr.write("{}\n".format(str(type(ex))))
                    sys.stderr.write("{}\n".format(ex.message))
                    sys.stderr.flush()
                else:
                    # sent OK, so clear down the points list
                    json_data = []

            if STOP:
                return


class InfluxLogger(BaseLogger):
    """
    Manages a threaded data logger posting to InfluxDB
    """
    def __init__(self, name, settings):
        self.queue = Queue.Queue()
        self.influx = InfluxLoggerThread(self.queue, name, settings)

    def put(self, data, timestamp=None):
        """
        Put data point on the queue, with timestamp. If timestamp not supplied,
        it will be set to current time.time()
        """
        if timestamp is None:
            timestamp = time.time()
        self.queue.put((timestamp, data))

    def start(self):
        """
        Start the uploader thread. No data will be posted until
        this is called.
        """
        self.influx.start()

    def stop(self):
        """
        Cleanly stop the uploader thread.
        Thread will stop when it reaches the termination message. This may
        not be immediate. All data on the queue to this point will be logged
        out first.
        """
        self.queue.put("STOP")
