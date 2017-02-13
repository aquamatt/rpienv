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
