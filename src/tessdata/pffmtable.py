# coding=utf-8
# See main file for licence
# pylint: disable=W0401,W0403
#
# by Mazoea s.r.o.
#

"""
    Expected features count.
"""
from .base import base
from .unicharset import unicharset


class pffmtable(base):

    name = "pffmtable"

    def __init__(self):
        self._v = {}

    def load(self, fin, start, end, parts):
        uniset = parts.get(unicharset.name)
        if 13 < len(parts._offsets) and 0 < parts._offsets[13]:
            reserved1 = fin.read_int4()
            shapetable_cutoffs = fin.read_struct(str(reserved1)+"H")
            start = -1

        for pos, line in enumerate(fin.readlines(start, end)):
            pos = line.rfind(" ")
            cls = line[:pos].strip()
            cutoff = int(line[pos:].strip())
            self._v[cls] = cutoff
            uniset[cls]["expected_features"] = cutoff

    def info(self, ftor, **kwargs):
        ftor(u"expected features count:")
        for m in [u"[%2s] %4d" % (self.u(k), v) for k, v in self._v.iteritems()]:
            ftor(m)

    def present(self):
        return 0 < len(self._v)
