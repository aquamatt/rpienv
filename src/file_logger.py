"""
Data logger that writes to file on disk
"""
import datetime
import time

from data_logger import BaseLogger


class FileLogger(BaseLogger):
    """
    Manages a synchronous data logger posting to a file
    """
    def __init__(self, name, fpath):
        self.name = name
        self.filename = fpath
        self.last = None

    def put(self, metric, values, timestamp=None):
        """
        Put data point(s) on the log
        """
        if timestamp is None:
            timestamp = time.time()
        now_date = datetime.datetime.fromtimestamp(timestamp)

        if self.last is None:
            self.last = timestamp
            return

        self.last = timestamp

        values = [str(d) for d in [now_date, timestamp]+values]

        with open(self.filename, "at") as df:
            df.write("{}\n".format(",".join(values)))
