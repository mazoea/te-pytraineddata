# coding=utf-8
# See main file for licence
# pylint: disable=W0401,W0403
#
# by Mazoea s.r.o.
#

"""
    Abstract reader
"""
import logging
from .utils import u_from_utf8
from collections import defaultdict


class base(object):
    logger = logging.getLogger("tessdata")
    MAX_OUTPUT = 50

    name = "Should have implemented this"

    def load(self, fin, start, end, parts):
        """ Load the file """
        raise NotImplementedError("Should have implemented this")

    def info(self, ftor, **kwargs):
        """ Log information about this object. """
        raise NotImplementedError("Should have implemented this")

    def log_info(self):
        """ Log information about this object. """
        def log(msg, *args):
            self.logger.info(msg, *args)
        self.info(log)

    def present(self):
        """ Is present in the loaded file? """
        raise NotImplementedError("Should have implemented this")

    @staticmethod
    def u(utf8_text):
        """ Return unicode """
        return u_from_utf8(utf8_text)

    def warning(self, msg, *args):
        self.logger.warning(msg, *args)

    def _assert(self, condition, error_msg, line):
        """ Output debug info. """
        if condition:
            return True
        self.warning(
            u"%s: [[assertion failed]] %s at line [%s]",
            self.name, error_msg, base.u(line)
        )
        return False


class parts_mockup(object):

    def __init__(self):
        self._offsets = 13 * []

    def get(self, key):
        return defaultdict(dict)


class fin_mockup(object):

    def __init__(self, fin):
        self._fin = fin

    def get(self, key):
        return defaultdict(dict)
