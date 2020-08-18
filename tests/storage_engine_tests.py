import os
import sys
import unittest

sys.path.insert(0, 'src')

from lib.storage_engine import StorageEngine
from lib.dataclasses.comic_data_class import ComicCase


class StorageEngineTest(unittest.TestCase):
    def setUp(self):
        self.sample_comic_case = ComicCase({'食戟之靈': {'01話': ['testurl1.jpg']}})
        self.storage_config = {
            'type': 'json',
            'storage_path': 'test_db.json'
        }

    def tearDown(self):
        os.remove('test_db.json')

    def test_json_storage_driver(self):
        se = StorageEngine(self.storage_config)
        se.save_all(self.sample_comic_case)

        assert se.get_all().to_raw() == self.sample_comic_case.to_raw()


if __name__ == '__main__':
    unittest.main(verbosity=2)
