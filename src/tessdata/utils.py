# coding=utf-8
# See main file for licence
# pylint: disable=W0401,W0403
#
# by Mazoea s.r.o.
#

"""
    Common utils
"""
import logging
_logger = logging.getLogger("tessdata")


def u_from_utf8(utf8_text):
    return utf8_text.decode("utf-8")
