import sys
import unittest

sys.path.insert(0, 'src')

from lib.dataclasses.comic_data_class import ComicCase
from lib.dataclasses.download_request import BasicDownloadRequest
from lib.crawl_engine import CrawlingDoer


class CodeGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.comic_case1 = ComicCase({'食戟之靈': {}})
        self.comic_case2 = ComicCase({'食戟之靈': {'01話': []}})
        self.comic_case3 = ComicCase({'食戟之靈': {'01話': ['testurl1.jpg']}})

        self.download_request = BasicDownloadRequest({
            '食戟之靈': {'01話': [], '02話': []}
        })

    def tearDown(self):
        pass

    def test_get_image1(self):
        cd1 = CrawlingDoer(self.comic_case1, self.download_request,
                           config={'code_dir_base': 'scripts', 'worker_info': {'type': 'direct'}})
        r_cc1 = cd1.do_request()

        assert r_cc1.get('食戟之靈').get('01話').data != []
        assert r_cc1.get('食戟之靈').get('02話').data != []

    def test_get_image2(self):
        cd2 = CrawlingDoer(self.comic_case2, self.download_request,
                           config={'code_dir_base': 'scripts', 'worker_info': {'type': 'direct'}})
        r_cc2 = cd2.do_request()
        assert r_cc2.get('食戟之靈').get('01話').data != []
        assert r_cc2.get('食戟之靈').get('02話').data != []

    def test_get_image3(self):
        cd3 = CrawlingDoer(self.comic_case3, self.download_request,
                           config={'code_dir_base': 'scripts', 'worker_info': {'type': 'direct'}})
        r_cc3 = cd3.do_request()
        assert r_cc3.get('食戟之靈').get('01話').data == self.comic_case3.get('食戟之靈').get('01話').data
        assert r_cc3.get('食戟之靈').get('02話').data != []


if __name__ == '__main__':
    unittest.main(verbosity=2)
