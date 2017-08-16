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
from .unicharset import unicharset


class normproto(base):
    name = "normproto"

    def __init__(self):
        from collections import OrderedDict
        self._v = {
            "params": [],
            "protos": OrderedDict(),
        }

    def load(self, fin, start, end, parts):
        lines = [x for x in fin.readlines(start, end)]
        pos = 0
        params_size = -1
        uniset = parts.get(unicharset.name)

        while pos < len(lines):
            line = lines[pos]
            if 0 == pos:
                params_size = int(line)
                pos += 1
                continue

            param = {
                "circular": False,
                "nonessential": False,
                "min": -1,
                "max": -1,
            }
            if pos <= params_size:
                # A character is described by multiple sets of extracted features.  Each
                # set contains a number of features of a particular type, for example, a
                # st of bays, or a set of closures, or a set of microfeatures.  Each
                # feature consists of a number of parameters.  All features within a
                # feature set contain the same number of parameters.  All circular
                # parameters are required to be the first parameters in the
                # feature.
                parts = line.split()
                if 'c' == parts[0][0]:
                    param["circular"] = True
                if 'e' == parts[1][0]:
                    param["nonessential"] = True
                param["min"] = float(parts[2])
                param["max"] = float(parts[3])
                self._v["params"].append(param)
                pos += 1
                continue
            parts = line.split()
            u = parts[0]

            self._assert(
                not uniset.present() or u in uniset,
                "invalid unicharset [%s]" % u,
                line
            )
            protos_count = int(parts[1])
            protos = []
            for i in range(protos_count):
                proto = {
                    "significant": False,
                    "style": None,
                    "sample_count": -1,
                }
                pos += 1
                line = lines[pos]
                parts = line.split()
                part_pos = 0
                if 's' == parts[part_pos][0]:
                    proto["significant"] = True
                part_pos += 1
                proto["style"] = parts[part_pos]
                part_pos += 1
                proto["sample_count"] = int(parts[part_pos])

                # new line
                pos += 1
                line = lines[pos]
                # CharNormY, CharNormLength, CharNormRx, CharNormRy
                proto["means"] = [float(x) for x in line.split()]

                # new line
                pos += 1
                line = lines[pos]
                parts = line.split()

                if "spherical" == proto["style"]:
                    self._assert(1 == len(parts),
                                 "invalid spherical definition", line)
                    proto["variance"] = float(parts[0])
                    proto["weight"] = 1.0 / proto["variance"]

                elif "elliptical" == proto["style"]:
                    proto["variance"] = [float(x) for x in parts]
                    proto["weight"] = [1.0 / x for x in proto["variance"]]

                elif "mixed" == proto["style"]:
                    # not really implemented
                    self.warning(
                        "%s:mixed mode not really supported", self.name)
                    proto["distributions"] = parts
                    pos += 1
                    line = lines[pos]
                    floats = line.split()

                protos.append(proto)

            self._v["protos"][u] = protos
            pos += 1
        return

    def info(self, ftor, **kwargs):
        pass

    def present(self):
        return 0 < len(self._v)

    #
    #

    def similar_protos(self, unichar, verbose=False, first_n=15):
        if unichar not in self._v["protos"]:
            return ["character not present in uniset"]
        p1 = self._v["protos"][unichar][0]
        assert p1["style"] == "elliptical"

        from collections import defaultdict
        res = defaultdict(list)
        for k, p2 in self._v["protos"].iteritems():
            for i, p2_proto in enumerate(p2):
                try:
                    result = normproto.match_protos(p1, p2_proto)
                    result = round(result, 3)
                except NotImplementedError:
                    result = u"not implemented"
                msg = u"sim = %7s comparing %s vs. %s in prototype #%d" % (
                    result, self.u(unichar), self.u(k), i)
                if verbose:
                    self.logger.info(msg)
                if not isinstance(result, basestring):
                    res[result].append(msg)
        arr = []
        for k in sorted(res.keys())[:first_n]:
            for msg in res[k]:
                arr.append(msg)
        return arr

    @staticmethod
    def match_protos(feature_set1, feature_set2):
        if feature_set2["style"] != "elliptical":
            raise NotImplementedError()

        kWidthErrorWeighting = 0.125
        means1 = feature_set1["means"]
        means2 = feature_set2["means"]
        # CharNormY, CharNormLength, CharNormRx, CharNormRy
        delta = means1[0] - means2[0]
        match = delta * delta * feature_set2["weight"][0]
        delta = means1[2] - means2[2]
        match += delta * delta * feature_set2["weight"][2]
        delta = means1[3] - means2[3]
        delta = delta * delta * feature_set2["weight"][3]
        delta *= kWidthErrorWeighting
        match += delta
        return match
