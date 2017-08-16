# coding=utf-8
# See main file for licence
#
# by Mazoea s.r.o.
#

"""
    Tesseract version.
"""
from .base import base


class version(base):

    name = "version"

    def __init__(self):
        self._v = ""

    def load(self, fin, start, end, parts):
        sz = fin.size()
        while start < sz:
            start += 1
            self._v += fin.read_char()

    def present(self):
        return 0 < len(self._v)

    def info(self, ftor, **kwargs):
        ftor("Version: %s", self._v)
