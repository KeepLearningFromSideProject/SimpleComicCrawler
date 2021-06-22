import sys
import unittest

sys.path.insert(0, 'src')

from lib.dataclasses.comic_data_class import ComicCase
from lib.dataclasses.download_request import BasicDownloadRequest
from lib.crawl_engine import CrawlingDoer


class MockedStorageEngine():
    def __init__(self, comic_case=ComicCase({})):
        self.cc = comic_case

    def get_all(self):
        return self.cc.to_raw()

    def save_all(self, comic_case):
        ori_raw = self.cc.to_raw()
        new_raw = comic_case.to_raw()

        for comic in new_raw:
            if comic not in ori_raw:
                ori_raw[comic] = {}

            for episode in new_raw[comic]:
                ori_raw[comic][episode] = new_raw[comic][episode]

        self.cc.from_raw(ori_raw)

    def get_comic_case(self):
        return self.cc

class CrawlingDoerTest(unittest.TestCase):
    def setUp(self):
        self.comic_case1 = ComicCase({'食戟之靈': {}})
        self.comic_case2 = ComicCase({'食戟之靈': {'01話': []}})
        self.comic_case3 = ComicCase({'食戟之靈': {'01話': ['testurl1.jpg']}})

        self.download_request = BasicDownloadRequest({
            '食戟之靈': {'01話': []}
        })

    def tearDown(self):
        pass

    def test_get_image1(self):
        se  = MockedStorageEngine(self.comic_case1)
        cd1 = CrawlingDoer(self.comic_case1, self.download_request,
                           config={'code_dir_base': 'scripts', 'worker_info': {'type': 'direct'}, 'max_download': 0},
                           storage_engine=se)
        cd1.do_request()
        r_cc1 = se.get_comic_case()

        assert r_cc1.get('食戟之靈').get('01話').data != []

    def test_get_image2(self):
        se  = MockedStorageEngine(self.comic_case2)
        cd2 = CrawlingDoer(self.comic_case2, self.download_request,
                           config={'code_dir_base': 'scripts', 'worker_info': {'type': 'direct'}, 'max_download': 0},
                           storage_engine=se)
        cd2.do_request()
        r_cc2 = se.get_comic_case()

        assert r_cc2.get('食戟之靈').get('01話').data != []

    def test_get_image3(self):
        se  = MockedStorageEngine(self.comic_case3)
        cd3 = CrawlingDoer(self.comic_case3, self.download_request,
                           config={'code_dir_base': 'scripts', 'worker_info': {'type': 'direct'}, 'max_download': 0},
                           storage_engine=se)
        cd3.do_request()
        r_cc3 = se.get_comic_case()

        assert set(r_cc3.get('食戟之靈').get('01話').data) == set(self.comic_case3.get('食戟之靈').get('01話').data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
