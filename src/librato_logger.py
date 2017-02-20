"""
Data logger that sends data in batches to Librato
"""
import logging
import Queue
import sys
import threading
import time

import librato
from librato.aggregator import Aggregator

from data_logger import BaseLogger


logger = logging.getLogger("librato-logger")


class LibratoLoggerThread(threading.Thread):
    """
    Post data to Librato in batches
    """
    PERIOD = 5

    def __init__(self, data_queue, metric_name, user, token):
        super(LibratoLoggerThread, self).__init__()
        self.data_queue = data_queue
        self.metric_name = metric_name
        self.librato = librato.connect(user, token)

    def run(self):
        aggregator = Aggregator(self.librato,
                                period=LibratoLoggerThread.PERIOD)
        start = time.time()
        while True:
            try:
                point = self.data_queue.get(block=True, timeout=1)
                if point == "STOP":
                    return
                timestamp, value = point
                aggregator.add(self.metric_name, value)
            except Queue.Empty:
                pass
            if time.time() - start >= LibratoLoggerThread.PERIOD:
                try:
                    aggregator.submit()
                except Exception as ex:
                    # ensure we don't crash out. Need to learn if anything
                    # else is to be done here.
                    sys.stderr.write("{}\n".format(ex.message))
                finally:
                    start = time.time()


class LibratoLogger(BaseLogger):
    """
    Manages a threaded data logger posting 1o Librato
    """
    def __init__(self, name, metric, user, token):
        self.name = name
        self.queue = Queue.Queue()
        self.librato = LibratoLoggerThread(self.queue, metric, user, token)

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
        self.librato.start()

    def stop(self):
        """
        Cleanly stop the uploader thread.
        Thread will stop when it reaches the termination message. This may
        not be immediate. All data on the queue to this point will be logged
        out first.
        """
        self.queue.put("STOP")
