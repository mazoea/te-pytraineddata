# coding=utf-8
# See main file for licence
# pylint: disable=W0401,W0403
#
# by Mazoea s.r.o.
#

"""
  Tesseract tessdata parser.
"""
import os
import logging
import struct

_logger = logging.getLogger("tessdata")
_logger.addHandler(logging.NullHandler())

__author__ = 'jm'
from .langdata import langdata
from .unicharset import unicharset
from .ambigs import ambigs
from .inttemp import inttemp
from .pffmtable import pffmtable
from .normproto import normproto
from .dawg import dawg
from .base import base
from _filereader import reader
from .lstm import lstm
from .version import version


class noop(base):

    def __init__(self, name):
        self.name = name

    def load(self, fin, start, end, parts):
        return

    def info(self, ftor, **kwargs):
        return

    def present(self):
        return False


class traineddata(object):

    dawg_names = [
        "punc_dawg",
        "word_dawg",
        "number_dawg",
        "freq_dawg",
        "fixed_length_dawg"
    ]

    # ctor
    #
    def __init__(self, file_str, ftor_progress=None, ftor_warning=None):

        self.file_parts = (
            langdata(),
            unicharset(),
            ambigs(),
            inttemp(),
            pffmtable(),
            normproto(),
            dawg(traineddata.dawg_names[0]),
            dawg(traineddata.dawg_names[1]),
            dawg(traineddata.dawg_names[2]),
            dawg(traineddata.dawg_names[3]),
            dawg(traineddata.dawg_names[4]),
            noop("cube_unicharset"),
            noop("cube_system_dawg"),
            #
            noop("shape"),
            dawg("bigram"),
            dawg("unambig"),
            noop("params model"),
            #
            lstm(),
            noop("new dawg"),
            noop("new dawg"),
            noop("new dawg"),
            unicharset(),
            noop("recorder"),
            version()

        )
        self._offsets = None
        self.input = file_str
        # logger style
        if ftor_warning is not None:
            for p in self.file_parts:
                p.warning = ftor_warning
        self.load(file_str, ftor_progress)

    #
    #
    def load(self, file_str, ftor=None):
        if not os.path.exists(file_str):
            raise IOError("file [%s] could not be found" % file_str)

        with reader(file_str) as fin:
            self._entries = fin.read_int4()
            self._offsets = fin.read_ints8(self._entries)

            for idx, part in enumerate(self.file_parts):
                if idx >= self._entries:
                    break
                try:
                    start, end = self.file_offsets(idx)
                except:
                    pass
                if 0 > start:
                    _logger.warn("traineddata does NOT CONTAIN [%s]", part.name)
                else:
                    _logger.warn("traineddata contains [%s]", part.name)
                    fin.seek(start)
                    try:
                        part.load(fin, start, end, self)
                    except Exception, e:
                        import traceback
                        tb = traceback.format_exc()
                        raise e
                # call ftor
                if ftor:
                    ftor(part, idx, self.file_parts)

    def get(self, name):
        for part in self.file_parts:
            if name == part.name:
                return part
        raise NotImplementedError("not implemented for [%s]" % name)

    def file_offsets(self, idx):
        s = self._offsets[idx]
        idx += 1
        while idx < self._entries and -1 == self._offsets[idx]:
            idx += 1
        e = self._offsets[idx] - 1 if idx < self._entries else -1
        return s, e

    def info(self):
        _logger.debug("%s", self)
        for idx, part in enumerate(self.file_parts):
            # if "inttemp" != part.name: continue
            _logger.info(10 * "=" + "\n%s\n" + 5 * "-", part.name)
            if part.present():
                part.log_info()
            else:
                _logger.info("not available")

    def __str__(self):
        return "<tessdata %s> #entries: %d" % (os.path.basename(self.input), len(self._offsets))


def get_unicode_name(c):
    import unicodedata
    name = None
    try:
        name = u".".join([unicodedata.name(x) for x in c])
    except:
        try:
            name = u".".join(c)
        except:
            pass
    return name
