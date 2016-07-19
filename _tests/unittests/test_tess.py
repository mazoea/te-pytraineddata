# coding=utf-8
# author: jmisutka
# version: 1.0
#
#
import unittest
#noinspection PyUnresolvedReferences
import testhelpers
import tessdata
from tessdata.normproto import normproto
from tessdata.inttemp import inttemp


#noinspection PyDocstring,PyUnresolvedReferences
# noinspection PyMethodOverriding
class Testutils( testhelpers.test_case ):

    def test_basic(self):
        """ test_basic """
        file_str, exists = testhelpers.files.in_data_dir("3.0/yid.traineddata")
        self.assertTrue(exists)
        t = tessdata.traineddata(file_str)
        t.info()
        from tessdata import inttemp
        inttmp = t.get(inttemp.name)
        #inttmp.store_all_proto_images("temp")

        progress_uploaded = 15
        # parse the traineddata
        progress_sum_parsing = 60

        def progress_ftor(part, pos, parts):
            progress = status.progress + (progress_sum_parsing / (len(parts) - pos))
            print progress

        def warning_ftor(msg, *args):
            data["warnings"].append(msg % args)

        # what with the data?
        for part in t.file_parts:
            text_arr = []
            images_arr = []

            def collector(msg, *_args):
                # % problem when empty args
                text_arr.append(msg % _args if 0 < len(_args) else msg)

            part.info(collector, max_to_print=1000)
            if part.name == normproto.name:
                self.handle_normproto(part, text_arr, images_arr)
            if part.name == inttemp.name:
                self.handle_inttemp(part, text_arr, images_arr)

    def handle_inttemp(self, part, text_arr, images_arr):
        first_n_images = 100
        import unicodedata
        import base64
        import io
        i = 0
        for c, im, _1 in part.proto_images():
            i += 1
            if i > first_n_images:
                text_arr.append("showing only first [%d] images" % first_n_images)
                break
            name = u".".join([unicodedata.name(x) for x in c])
            buf = io.BytesIO()
            im.save(buf, 'png')
            img_data_base64 = base64.b64encode(buf.getvalue())
            images_arr.append("%s?%s" % (name, img_data_base64))

    def handle_normproto(self, part, text_arr, images_arr):
        text_arr.append(u"cluster similarities (+/-)")
        for u in u"abcdefghijklmnopqrstuvxyz":
            text_arr += part.similar_protos(u)

if __name__ == '__main__':
    unittest.main()