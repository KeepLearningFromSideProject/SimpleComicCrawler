"""
crawl engine
"""

import os
import subprocess

def generate_code_get_comic_home(code_dir_base, comic_name):
    code_path = os.path.join(code_dir_base, 'get_comic_home.py')
    with open(code_path, 'r') as src:
        return 'comic_name = "{}"\n{}'.format(comic_name, src.read())

def generate_code_get_episode_urls(code_dir_base, comic_home):
    code_path = os.path.join(code_dir_base, 'get_episode_urls.py')
    with open(code_path, 'r') as src:
        return 'comic_url = "{}"\n{}'.format(comic_home, src.read())

def generate_code_get_images(code_dir_base, episode_url):
    code_path = os.path.join(code_dir_base, 'get_images.py')
    with open(code_path, 'r') as src:
        return 'episode_url = "{}"\n{}'.format(episode_url, src.read())
