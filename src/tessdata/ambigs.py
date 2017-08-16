# coding=utf-8
# See main file for licence
# pylint: disable=W0401,W0403
#
# by Mazoea s.r.o.
#

"""
    Tesseract ambigs.
"""
from .base import base
from .unicharset import unicharset


class ambigs(base):
    """
        See ccutil/ambigs.cpp
    """
    name = "ambigs"

    def __init__(self):
        self._v = []

    def load(self, fin, start, end, parts):
        uniset = parts.get(unicharset.name)

        def validate(chars, s, e, l):
            while s < e:
                token = chars[s]
                self._assert(token in uniset,
                             "used token not in unicharset", l)
                s += 1

        version = -1
        for pos, line in enumerate(fin.readlines(start, end)):
            if 0 == pos:
                # +- ccutil/ambigs.cpp:84
                if "v" == line[0]:
                    version = int(line[1:])
                    if 1 < version:
                        self.warning(
                            "%s in a not supported format" % self.name)
                        return
                    continue

            ambig = {
                "always": None,
                "from": None,
                "to": None,
            }
            parts = line.split()
            if not self._assert(1 != len(parts), "illegal ambiguity", line):
                continue
            try:
                chars_len = int(parts[0])
                validate(parts, 1, chars_len, line)
                from_start = 1
                from_end = from_start + chars_len
                s = from_start
                ambig["from"] = "".join(parts[from_start:from_end])
                self._assert(len(parts) > chars_len, "invalid length", line)
                repl_len = int(parts[from_end].strip())
                repl_start = from_end + 1
                repl_end = repl_start + repl_len
                self._assert(len(parts) > chars_len + 1 + repl_len,
                             "invalid length", line)
                validate(parts, chars_len + 1, chars_len + 1 + repl_len, line)
            except:
                self.warning("invalid ambigs line: %s", line)
                continue

            ambig["to"] = "".join(parts[repl_start:repl_end])
            if 0 < version:
                self._assert(len(parts) == 1 + chars_len + 1 + repl_len + 1,
                             "invalid length", line)
                ambig["always"] = "1" == parts[-1]

            self._v.append(ambig)

    def info(self, ftor, **kwargs):
        for msg in \
                [u"%6s %5s -> %5s" % (
                    u"always" if a["always"] else u"",
                    self.u(a["from"]),
                    self.u(a["to"]),
                ) for a in self._v]:
            ftor(msg)

    def present(self):
        return 0 < len(self._v)
