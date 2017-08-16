# coding=utf-8
# author: jm
import unittest
# noinspection PyUnresolvedReferences
import testhelpers
import tessdata
from tessdata.normproto import normproto
from tessdata.inttemp import inttemp


# noinspection PyDocstring,PyUnresolvedReferences
# noinspection PyMethodOverriding
class Testtess4(testhelpers.test_case):

    def test_basic(self):
        """ test_basic """
        file_str, exists = testhelpers.files.in_data_dir(
            "4.0/Latin.traineddata")
        if exists:
            t = tessdata.traineddata(file_str)
            t.info()


if __name__ == '__main__':
    unittest.main()
