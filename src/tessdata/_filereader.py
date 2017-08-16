# coding=utf-8
# See main file for licence
# pylint: disable=W0401,W0403
#
# by Mazoea s.r.o.
#

"""
    Filereader
"""
import os
import struct


class reader(object):
    size_of_int8 = 1
    size_of_int16 = 2
    size_of_int32 = 4
    size_of_int64 = 8

    def __init__(self, file_str):
        self.f = open(file_str, "rb")

    def read_bytes(self, cnt):
        return self.f.read(cnt)

    def read_string(self):
        str_len = self.read_int4()
        s = self.read_bytes(str_len)
        return struct.unpack("%ds" % str_len, s)[0]

    def read_char(self):
        s = self.read_bytes(reader.size_of_int8)
        return struct.unpack("c", s)[0]

    def read_byte(self):
        s = self.read_bytes(reader.size_of_int8)
        return struct.unpack("b", s)[0]

    def read_int2(self):
        s = self.read_bytes(reader.size_of_int16)
        return struct.unpack("h", s)[0]

    def read_int4(self):
        s = self.read_bytes(reader.size_of_int32)
        return struct.unpack("i", s)[0]

    def read_ints8(self, cnt):
        s = self.read_bytes(cnt * reader.size_of_int64)
        return struct.unpack(cnt * "q", s)

    def read_struct(self, specification):
        s = self.read_bytes(struct.calcsize(specification))
        return struct.unpack(specification, s)

    def read_namedtuple(self, specification, cls):
        s = self.read_bytes(struct.calcsize(specification))
        return cls._make(struct.unpack(specification, s))

    def seek(self, offset):
        self.f.seek(offset)

    def readlines(self, start_offset, end_offset):
        if -1 < start_offset:
            self.seek(start_offset)
            pos = start_offset
        else:
            pos = self.f.tell()
        for line in self.f:
            pos += len(line)
            if pos > end_offset + 1:
                return
            if 0 == len(line.strip()):
                continue
            yield line.strip()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.f.close()

    def size(self):
        orig = self.f.tell()
        self.f.seek(0, os.SEEK_END)
        size = self.f.tell()
        self.f.seek(orig, os.SEEK_SET)
        return size
