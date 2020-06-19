import sys
import unittest
import subprocess

sys.path.insert(0, '../src')

from lib.crawl_engine import generate_code_get_comic_home
from lib.crawl_engine import generate_code_get_episode_urls
from lib.crawl_engine import generate_code_get_images

def execute_code(code):
    res = subprocess.run(
        ["python3"],
        stdout=subprocess.PIPE,
        input=bytes(code, 'utf-8')
    )

    return res.stdout.decode('utf-8')

class CodeGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.comic_name = '食戟之靈'
        self.comic_url = 'https://comicbus.com/html/9337.html'
        self.episode_url = 'https://comicbus.live/online/a-9337.html?ch=1'

    def tearDown(self):
        pass

    def test_get_comic_home(self):
        code = generate_code_get_comic_home('../scripts', self.comic_name)
        execute_code(code)

    def test_get_episode_urls(self):
        code = generate_code_get_episode_urls('../scripts', self.comic_url)
        execute_code(code)

    def test_get_images(self):
        code = generate_code_get_images('../scripts', self.episode_url)
        execute_code(code)

if __name__ == '__main__':
    unittest.main(verbosity=2)
