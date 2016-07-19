# coding=utf-8
# See main file for licence
# pylint: disable=W0401,W0403
#
# by Mazoea s.r.o.
#

"""
    Tesseract configuration.
"""
from .base import base


class langdata(base):

    name = "lang_config"

    def __init__(self):
        self._v = {
            "comments": [],
            "configuration": {},
        }

    def load(self, fin, start, end, parts):
        for line in fin.readlines(start, end):
            if "#" == line[0]:
                self._v["comments"].append(self.u(line))
                continue
            elif len(line) < 3:
                continue
            splits = line.split()
            if 2 != len(splits):
                self.warning(
                    u"%s: does not contain valid parameter set: [%s]",
                    self.name, self.u(line[:self.MAX_OUTPUT])
                )
                continue
            # valid configuration
            self._v["configuration"][splits[0]] = self.u(splits[1])

    def info(self, ftor, **kwargs):
        if 0 < len(self._v["comments"]):
            ftor(u"comments:")
            for comment in self._v["comments"]:
                ftor(comment)
        if 0 < len(self._v["configuration"]):
            ftor(u"configuration:")
            for m in ["%s = %s" % (k, v)
                      for k, v in self._v["configuration"].iteritems()]:
                ftor(m)

    def present(self):
        return 0 < len(self._v)
