# coding=utf-8
# See main file for licence
# pylint: disable=W0401,W0403
#
# by Mazoea s.r.o.
#

"""
    .
"""
import math
import os
from .base import base, parts_mockup
from ._filereader import reader
from . import _constants as tesseract
from . import unicharset


class inttemp(base):
    """
    Class:
        Short for Classification, usually in the sense that an
        outline or several outlines had their features extracted
        and these features matched a particular built-in template.

    Pruners:
        The class pruner is a pre-classifier that is used to create
        a short-list of classification candidates (pruning the possible
        classes) so that the full distance metric can be calculated on
        the short-list without taking excessive time, instead of
        exhaustively matching against each character possibility.
        The class pruner uses a faster, but approximate method of
        matching the features, so while it does make mistakes,
        the mistakes are rare.
    """

    name = "inttemp"

    def __init__(self):
        self.uniset = None
        self._v = {
            "pruners": [],
            "classes": [],
            "fonts": [],
            "fontsets": [],
        }

    @staticmethod
    def load_from_file(filename):
        inst = inttemp()
        with open(filename, mode="r") as fin:
            r = reader(filename)
            inst.load(r, 0, r.size(), parts_mockup())
        return inst

    def load(self, fin, start, end, parts):
        self.uniset = parts.get(unicharset.name)
        unicharset_size = fin.read_int4()
        classes_size = fin.read_int4()
        pruners_size = fin.read_int4()
        if classes_size < 0:
            # version id
            version_id = -classes_size
            classes_size = fin.read_int4()
            self._v["version_id"] = version_id
        if self._v["version_id"] < 4:
            self.warning("%s: too old version - not supported", self.name)
            return

        # pruners
        #
        for n in range(pruners_size):
            self._v["pruners"].append(
                fin.read_struct(str(tesseract.CLASS_PRUNER_STRUCT_SIZE) + "I")
            )
            # class_pruner = \
            #     [[[
            #           [0 for l in range(tesseract.WERDS_PER_CP_VECTOR)]
            #           for k in range(tesseract.NUM_CP_BUCKETS)
            #           ] for j in range(tesseract.NUM_CP_BUCKETS)
            #       ] for i in range(tesseract.NUM_CP_BUCKETS)
            #      ]
            # raw_pos = 0
            # for i in range(tesseract.NUM_CP_BUCKETS):
            #     ci = class_pruner[i]
            #     for j in range(tesseract.NUM_CP_BUCKETS):
            #         cj = ci[j]
            #         for k in range(tesseract.NUM_CP_BUCKETS):
            #             ck = cj[k]
            #             for l in range(tesseract.WERDS_PER_CP_VECTOR):
            #                 ck[l] = class_pruner_raw[raw_pos]
            #                 raw_pos += 1
            # pruners.append(class_pruner)
            # class_pruner = class_pruner_raw = ci = cj = ck = None

        # class
        #
        from collections import namedtuple
        struct_class = namedtuple("Class", "NumProtos NumProtoSets NumConfigs")
        struct_int_proto_struct = namedtuple("int_proto_struct", "a b c angle")

        for n in range(classes_size):
            specification = "HBB"
            cls = fin.read_namedtuple(specification, struct_class)
            config_lengths = []
            if 0 < cls.NumConfigs:
                config_lengths = fin.read_struct(str(cls.NumConfigs) + "H")

            # length of XX for each of the prototype
            proto_lengths = []
            if 0 < cls.NumProtoSets:
                proto_lengths = fin.read_struct(
                    str(cls.NumProtoSets * tesseract.PROTOS_PER_PROTO_SET) + "B")
            proto_sets = []
            for m in range(cls.NumProtoSets):
                # read PROTO_SET_STRUCT
                proto_pruner = fin.read_struct(
                    str(tesseract.PROTO_PRUNER_SIZE) + "I")
                proto_set = {
                    "pruners": proto_pruner,
                    "protos": [],
                }
                for i in range(tesseract.PROTOS_PER_PROTO_SET):
                    p = fin.read_namedtuple("bBbB", struct_int_proto_struct)
                    configs = fin.read_struct(
                        str(tesseract.WERDS_PER_CONFIG_VEC) + "I")
                    proto_set["protos"].append({
                        "a": p.a,
                        "b": p.b,
                        "c": p.c,
                        "angle": p.angle,
                        "configs": configs,
                    })
                proto_sets.append(proto_set)
            font_set_id = fin.read_int4()
            self._v["classes"].append({
                "configlengths": config_lengths,
                "protolengths": proto_lengths,
                "protosets": proto_sets,
                "fontset": font_set_id,
            })

        #
        #
        reserved = fin.read_int4()
        size_used = fin.read_int4()
        for i in range(size_used):
            size = fin.read_int4()
            font_name = fin.read_bytes(size)
            properties = fin.read_int4()
            self._v["fonts"].append({
                "name": font_name,
                "properties": properties,
                "spacing": [],
            })

        # v5
        #
        if 5 <= self._v["version_id"]:
            reserved = fin.read_int4()
            size_used = fin.read_int4()
            fontspacinginfo = namedtuple(
                "fontspacinginfo", "x_gap_before x_gap_after kern_size")
            for i in range(size_used):
                vec_size = fin.read_int4()
                for j in range(vec_size):
                    fsi = fin.read_namedtuple("HHi", fontspacinginfo)
                    if 0 > fsi.kern_size:
                        continue
                    if 0 < fsi.kern_size:
                        reserved1 = fin.read_int4()
                        kerned_unichar_ids = fin.read_struct(
                            str(reserved1) + "i")
                        reserved2 = fin.read_int4()
                        kerned_x_gaps = fin.read_struct(str(reserved2) + "H")
                    self._v["fonts"][i]["spacing"].append(fsi)

        # v5
        # - fontsets
        reserved = fin.read_int4()
        size_used = fin.read_int4()
        # Every class (character) owns a FontSet that represents all the fonts that can
        # render this character.
        # Since almost all the characters from the same script share the same set of
        # fonts, the sets are shared over multiple classes (see
        # Classify::fontset_table_). Thus, a class only store an id to a set.
        # Because some fonts cannot render just one character of a set, there are a
        # lot of FontSet that differ only by one font. Rather than storing directly
        # the FontInfo in the FontSet structure, it's better to share FontInfos among
        # FontSets (Classify::fontinfo_table_).
        for i in range(size_used):
            fs_size = fin.read_int4()
            # FontInfo ids
            configs = []
            for j in range(fs_size):
                configs.append(fin.read_int4())
            self._v["fontsets"].append(configs)

    def info(self, ftor, **kwargs):
        verbose = kwargs.get("verbose", False)
        ftor("fonts:")
        for font in self._v["fonts"]:
            ftor(font["name"])
            for spacing in font["spacing"]:
                if verbose:
                    ftor("\tx_gap_before:%s, x_gap_after:%s, kern_size:%s",
                         spacing.x_gap_before,
                         spacing.x_gap_after,
                         spacing.kern_size)

        # newest version uses shapeid
        # ftor("fontsets:")
        # for i, fontset in enumerate(self._v["fontsets"]):
        #     names = []
        #     for idx in fontset:
        #         names.append(self.u(self._v["fonts"][idx]["name"]))
        #     if 0 == len(names):
        #         names= ["..."]
        #     ftor("%3d. %s", i, u",".join(names))

        if verbose:
            for i, cls in enumerate(self._v["classes"]):
                ftor("%3d. set - fontset %d", i, cls["fontset"])
                ftor("\tconfig lengths: %s", " ".join(
                    ["%4d" % x for x in cls["configlengths"]]
                ))
                ftor("\tproto lengths: %s", " ".join(
                    ["%4d" % x for x in cls["protolengths"]]
                ))
                for j, protos_classes in enumerate(cls["protosets"]):
                    ftor("\tclass #%d", j)
                    for k, proto in enumerate(protos_classes["protos"]):
                        ftor(
                            "\t\t%3d. a:%4d b:%4d c:%4d angle:%4d configs:%s",
                            k, proto["a"], proto["b"], proto[
                                "c"], proto["angle"],
                            " ".join(["%6s" % x for x in proto["configs"]])
                        )

    def present(self):
        return 0 < len(self._v)

    #
    #
    def store_all_proto_images(self, output_dir=None):
        from . import get_unicode_name
        invalid_name = 0
        for c, im, draw in self.proto_images():
            filename = get_unicode_name(c)
            if filename is None:
                filename = u"invalid_name-%d" % invalid_name
                invalid_name += 1
            filename = u"protos.%s.png" % filename
            output_file = os.path.join(output_dir or ".", filename)
            im.save(output_file)

    def proto_images(self):
        from PIL import Image, ImageDraw
        from PIL import ImageFont
        font_size = 16
        font = None
        for name in ("arial.ttf", "DejaVuSans.ttf"):
            try:
                font = ImageFont.truetype(name, font_size)
                break
            except:
                pass
        if font is None:
            font = ImageFont.load_default()

        im_size = 384, 384
        for i, cls in enumerate(self._v["classes"]):
            c = self.u(self.uniset[i]["char"])

            im = Image.frombytes(
                'RGB', im_size, "\xff\xff\xff" * im_size[0] * im_size[1])
            draw = ImageDraw.Draw(im)

            success = False

            colors = (
                (255, 0, 0),
                (0, 0, 255),
                (0, 255, 0),
                (255, 255, 0),
                (0, 255, 255),
                (255, 0, 255),
            )

            def get_colour(bucket):
                return colors[bucket] if bucket < len(colors) else (128, 128, 0)

            # display protos
            s = "Protos displayed: "
            for j, protoset in enumerate(cls["protosets"]):
                for k in range(len(protoset["protos"])):
                    success = self._display_int_proto(
                        cls,
                        j * tesseract.PROTOS_PER_PROTO_SET + k,
                        draw,
                        im_size,
                        get_colour(j)
                    )
                s += "%d-th [%d] " % (j, len(protoset["protos"]))

            # display expected features
            draw.text((10, font_size), s, (0, 0, 0), font=font)
            s = "Expected features [%d]" % self.uniset[
                i].get("expected_features", -1)
            draw.text((10, font_size * 2), s, (0, 0, 0), font=font)

            if success:
                try:
                    yield (c, im, draw)
                except Exception, e:
                    self.logger.info(
                        u"not showing prototype %s - %s", c, repr(e))
            else:
                if 0 != i:
                    self.logger.info(u"not showing prototype for [%s]", c)

    def _display_int_proto(self, cls, proto_id, draw, im_size, colour):
        """
            intproto.cpp
        """

        def get_proto_set(pid):
            return pid / tesseract.PROTOS_PER_PROTO_SET

        def get_proto_idx(pid):
            return pid % tesseract.PROTOS_PER_PROTO_SET

        def get_pruner_mask(pid):
            def PPrunerBitIndexFor(I):
                return I % tesseract.PROTOS_PER_PP_WERD

            return 1 << PPrunerBitIndexFor(pid)

        def get_pruner_word_index(pid):
            return (pid % tesseract.PROTOS_PER_PROTO_SET) \
                / tesseract.PROTOS_PER_PP_WERD

        proto_set = cls["protosets"][get_proto_set(proto_id)]
        protos = proto_set["protos"]
        if 0 == len(protos):
            return False
        proto = protos[get_proto_idx(proto_id)]
        Length = cls["protolengths"][proto_id] * \
            tesseract.PICO_FEATURE_LENGTH * \
            tesseract.INT_CHAR_NORM_RANGE
        proto_mask = get_pruner_mask(proto_id)
        proto_word_index = get_pruner_word_index(proto_id)

        def update_range(x, lower_bound, upper_bound):
            if x < lower_bound:
                lower_bound = x
            if x > upper_bound:
                upper_bound = x
            return lower_bound, upper_bound

        # find the x and y extent of the proto from the proto pruning table
        Xmin = Ymin = tesseract.NUM_PP_BUCKETS
        Xmax = Ymax = 0

        def get_proto_pruner(proto_pruner, x, y, z):
            return proto_pruner[x * tesseract.NUM_PP_BUCKETS * tesseract.WERDS_PER_PP_VECTOR
                                + y * tesseract.WERDS_PER_PP_VECTOR
                                + z]

        proto_pruner = proto_set["pruners"]
        for i in range(tesseract.NUM_PP_BUCKETS):
            pp_x = get_proto_pruner(
                proto_pruner, tesseract.PRUNER_X, i, proto_word_index)
            pp_y = get_proto_pruner(
                proto_pruner, tesseract.PRUNER_Y, i, proto_word_index)
            if proto_mask & pp_x:
                Xmin, Xmax = update_range(i, Xmin, Xmax)
            if proto_mask & pp_y:
                Ymin, Ymax = update_range(i, Ymin, Ymax)

        X = (Xmin + Xmax + 1) / 2.0 * tesseract.PROTO_PRUNER_SCALE
        Y = (Ymin + Ymax + 1) / 2.0 * tesseract.PROTO_PRUNER_SCALE
        Dx = (Length / 2.0) * \
            math.cos((proto["angle"] / 256.0) * 2.0 * math.pi)
        Dy = (Length / 2.0) * \
            math.sin((proto["angle"] / 256.0) * 2.0 * math.pi)

        # different x,y base
        start = int(X - Dx), im_size[1] - int(Y - Dy)
        to = int(X + Dx), im_size[1] - int(Y + Dy)
        draw.line(start + to, fill=colour, width=3)
        return True
