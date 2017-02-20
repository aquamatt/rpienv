"""
Data logger that writes to file on disk
"""
import datetime
import time
from types import ListType

from data_logger import BaseLogger


class FileLogger(BaseLogger):
    """
    Manages a synchronous data logger posting to a file
    """
    def __init__(self, name, fpath):
        self.name = name
        self.filename = fpath
        self.last = None

    def put(self, data, timestamp=None):
        """
        Put data point on the log
        """
        if timestamp is None:
            timestamp = time.time()
        now_date = datetime.datetime.fromtimestamp(timestamp)

        if self.last is None:
            self.last = timestamp
            return

        delta = timestamp - self.last
        self.last = timestamp

        if type(data) is not ListType:
            data = [data]

        data.insert(0, delta)
        data = [str(d) for d in [now_date, timestamp]+data]

        with open(self.filename, "at") as df:
            df.write("{}\n".format(",".join(data)))
