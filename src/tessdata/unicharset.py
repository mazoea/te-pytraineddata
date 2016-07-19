# coding=utf-8
# See main file for licence
# pylint: disable=W0401,W0403
#
# by Mazoea s.r.o.
#

"""
    Set of recognisable characters
"""
from .base import base


class unicharset(base):
    """
    TODO:  ambigs should be inserted to unicharset as well
    """

    name = "unicharset"
    properties = (
        (0x01, "alpha"),
        (0x02, "lower"),
        (0x04, "upper"),
        (0x08, "digit"),
        (0x10, "punc"),
    )

    def __init__(self):
        from collections import OrderedDict
        self._v = OrderedDict()

    def load(self, fin, start, end, parts):
        for pos, line in enumerate(fin.readlines(start, end)):
            if 0 == pos:
                # read count
                cnt = int(line)
                continue

            # one unichar
            unichar = {
                "char": None,
                "min_bottom": 0,
                "min_top": 0,
                "max_bottom": 255,
                "max_top": 255,
                "properties": set(),
                "script": None,
                # id in unicharset of the opposite case
                "other_case_id": None,
                #
                "is_n_gram": False,
                "comment": "",
                # filled in in pffmtable
                "expected_features": -1
            }

            # strip comment
            if -1 != line[2:].find('#'):
                hash_pos = line.find('#', 3)
                unichar["comment"] = line[hash_pos + 1:].strip()
                line = line[:hash_pos].strip()
            parts = line.split(" ")
            char = parts[0]

            # NULL is space
            if 4 == len(char) and "NULL" == char:
                char = " "

            # get property names if any
            unichar["char"] = char
            try:
                prop = int(parts[1], 16)
                for (v, key) in self.properties:
                    if 0 != (prop & v):
                        unichar["properties"].add(key)
            except:
                pass

            if 2 > len(parts) or 8 < len(parts):
                self.warning(
                    "%s: invalid line format [%s]", self.name, line)
                continue

            # different types
            if 2 == len(parts):
                continue

            pos = 2
            end_pos = -1
            if 8 == len(parts):
                unichar["normed"] = parts[end_pos]
                end_pos -= 1
            if 7 <= len(parts):
                unichar["mirror"] = int(parts[end_pos])
                end_pos -= 1
                unichar["direction"] = parts[end_pos]
            if 5 <= len(parts):
                min_max_parts = parts[pos].split(",")
                self._assert(4 == len(min_max_parts) or 10 == len(min_max_parts),
                             "invalid min max specified", line)
                unichar["min_bottom"] = int(min_max_parts[0])
                unichar["max_bottom"] = int(min_max_parts[1])
                unichar["min_top"] = int(min_max_parts[2])
                unichar["max_top"] = int(min_max_parts[3])
                if 10 == len(min_max_parts):
                    unichar["width"] = int(min_max_parts[4])
                    unichar["width_sd"] = int(min_max_parts[5])
                    unichar["bearing"] = int(min_max_parts[6])
                    unichar["bearing_sd"] = int(min_max_parts[7])
                    unichar["advance"] = int(min_max_parts[8])
                    unichar["advance_sd"] = int(min_max_parts[9])
                pos += 1

            if 4 <= len(parts):
                unichar["script"] = parts[pos]
                pos += 1

            if 3 <= len(parts):
                unichar["other_case_id"] = parts[pos]
                pos += 1

            # add it
            self._v[char] = unichar

    def present(self):
        return 0 < len(self._v)

    def info(self, ftor, **kwargs):
        for pos, v in enumerate(self._v.values()):
            extra = u""
            if "width" in v:
                extra += " width:%4d" % v["width"]
            if "normed" in v:
                extra += " normed:%4s" % self.u(v["normed"])
            if "mirror" in v:
                mirror_u = self[v["mirror"]]["char"]
                extra += " mirror char:%4s" % self.u(mirror_u)
            if "direction" in v:
                extra += " direction:%15s" % v["direction"]
            ftor(
                u"%3d. %4s [%20s] # %10s" % (
                    pos, self.u(v["char"]), u" ".join(v["properties"]),
                    self.u(v["comment"])
                )
            )
            ftor(
                u"            top:<%4d;%4d> bottom:<%4d;%4d> %s]" % (
                    v["min_top"], v["max_top"],
                    v["min_bottom"], v["max_bottom"],
                    extra
                )
            )

    #
    #

    @staticmethod
    def get_direction(d):
        # unicharset.h
        return [
            "LEFT_TO_RIGHT",
            "RIGHT_TO_LEFT",
            "EUROPEAN_NUMBER",
            "EUROPEAN_NUMBER_SEPARATOR",
            "EUROPEAN_NUMBER_TERMINATOR",
            "ARABIC_NUMBER",
            "COMMON_NUMBER_SEPARATOR",
            "BLOCK_SEPARATOR",
            "SEGMENT_SEPARATOR",
            "WHITE_SPACE_NEUTRAL",
            "OTHER_NEUTRAL",
            "LEFT_TO_RIGHT_EMBEDDING",
            "LEFT_TO_RIGHT_OVERRIDE",
            "RIGHT_TO_LEFT_ARABIC",
            "RIGHT_TO_LEFT_EMBEDDING",
            "RIGHT_TO_LEFT_OVERRIDE",
            "POP_DIRECTIONAL_FORMAT",
            "DIR_NON_SPACING_MARK",
            "BOUNDARY_NEUTRAL",
            "CHAR_DIRECTION_COUNT",
        ][d]

    #
    #

    def __contains__(self, char):
        return char in self._v

    def __getitem__(self, idx):
        if isinstance(idx, basestring):
            if "NULL" == idx:
                idx = " "
            return self._v[idx]
        else:
            return self._v.values()[idx]

    def __len__(self):
        return len(self._v)
