# coding=utf-8
# See main file for licence
# pylint: disable=W0401,W0403
#
# by Mazoea s.r.o.
#

"""
    Tesseract dawg.
"""
from __future__ import print_function
from .base import base
from .unicharset import unicharset
from . import _constants as tesseract
import math


class dawg(base):
    def __init__(self, name):
        self.name = name
        self._v = []
        #
        self.dawg = None

    def load(self, fin, start, end, parts):
        # read header
        magic = fin.read_int2()
        uniset_size = fin.read_int4()
        num_edges = fin.read_int4()
        # read edges
        self._v = fin.read_struct(str(num_edges) + "q")
        # abstract dawg
        self.dawg = tess_dawg(self._v, parts.get(unicharset.name))

    def info(self, ftor, **kwargs):
        max_to_print = kwargs.get("max_to_print", 100)

        def print_max(i, w):
            if i > max_to_print:
                raise GeneratorExit()
            ftor(u"%7d. %s" % (i, w))
        try:
            self.iter_words(print_max)
        except BaseException, e:
            ftor("...printing the first %d entries only..." % max_to_print)
            pass

    def present(self):
        return 0 < len(self._v)

    #
    #
    #

    def iter_words(self, ftor):
        """ Iterate from the beginning. """
        self._iter(0, "", [0], ftor)

    def print_words(self):
        self.iter_words(lambda i, w: print(w))

    #
    #
    def _iter(self, idx, word_part, arr_pos, ftor):
        """ Recursively get word for word. """
        if not self.present():
            return
        arr = self.dawg.unichar_ids_of(idx)
        for idx in arr:
            w = word_part
            w += self.dawg.idx2char(idx)
            if self.dawg.end_of_word(idx):
                ftor(arr_pos[0], self.u(w))
                arr_pos[0] += 1
            next_idx = self.dawg.next_node(idx)
            if 0 != next_idx:
                self._iter(next_idx, w, arr_pos, ftor)


class tess_dawg(object):
    """
        Tesseract dawg read only minimal implementation.
    """

    def __init__(self, edges, uniset):
        self.edges = edges
        self.uniset = uniset
        unicharset_size = len(uniset)
        self.flag_start_bit = int(
            math.ceil(
                math.log(float(unicharset_size)) / math.log(2.0)
            )
        )
        self.next_node_start_bit = self.flag_start_bit + tesseract.NUM_FLAG_BITS
        self.letter_mask = ~(~0 << self.flag_start_bit)
        self.next_node_mask = (~0 << (self.flag_start_bit + tesseract.NUM_FLAG_BITS)) & 0xffffffffffffffff
        self.flags_mask = ~(self.letter_mask | self.next_node_mask) & 0xffffffffffffffff

    def idx2char(self, idx):
        """ Get character from unicharset based on its index. """
        id_ = self.unichar_id_from_edge_rec(self.edges[idx])
        return self.uniset[id_]["char"]

    def next_node_from_edge_rec(self, e):
        return (e & self.next_node_mask) >> self.next_node_start_bit

    def end_of_word_from_edge_rec(self, e):
        """ Returns true if this edge marks the end of a word. """
        return (e & (tesseract.WERD_END_FLAG << self.flag_start_bit)) != 0

    def end_of_word(self, idx):
        return self.end_of_word_from_edge_rec(self.edges[idx])

    def unichar_id_from_edge_rec(self, e):
        return (e & self.letter_mask) >> tesseract.LETTER_START_BIT

    def edge_occupied(self, idx):
        return self.edges[idx] != self.next_node_mask

    def last_edge(self, idx):
        return (self.edges[idx] & (tesseract.MARKER_FLAG << self.flag_start_bit)) != 0

    def next_node(self, idx):
        return self.next_node_from_edge_rec(self.edges[idx])

    def unichar_ids_of(self, idx):
        ret = []
        if not self.edge_occupied(idx):
            return ret
        while True:
            ret.append(idx)
            if self.last_edge(idx):
                break
            idx += 1
        return ret
