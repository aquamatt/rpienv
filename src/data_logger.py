from import_utils import import_module_from
import sys


class BaseLogger(object):
    """
    Base data logger

    Looks a bit Java-esque, what with the empty methods, but it helps keep
    standardised classes if some methods that aren't needed in all
    implementations have an empty version.
    """
    def put(self, data, timestamp=None):
        pass

    def start(self):
        pass

    def stop(self):
        pass


class DataLogger(object):
    """
    Manage all loggers as configured in logger_config settings.
    """
    def __init__(self):
        self.loggers = []

    def init(self, logger_config):
        """
        Initialise all the loggers
        """
        for logger, config in logger_config.items():
            if 'enabled' in config:
                if config['enabled'] is False:
                    continue
                del config['enabled']

            try:
                log_class = config['logger']
                _module = import_module_from(log_class)
                del config['logger']

                self.loggers.append(_module(logger, **config))
                print("Installed logger: {}".format(logger))
            except Exception as ex:
                sys.stderr.write("Error importing {}: {}\n"
                                 .format(log_class, ex.message))

    def put(self, metric, values, timestamp=None):
        """
        Metric is a group name, values is a list of (value-name, value) pairs,
        and timestamp is an optional system timestamp.
        """
        for logger in self.loggers:
            logger.put(metric, values, timestamp)

    def start(self):
        for logger in self.loggers:
            logger.start()

    def stop(self):
        for logger in self.loggers:
            logger.stop()
