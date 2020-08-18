"""
crawl engine
"""

import os
import json
import urllib
import requests
import subprocess


class CrawlEngine:
    def __init__(self, config={
        'code_dir_base': '../scripts',
        'worker_info': {'type': 'direct'}
    }):
        self.config = config

    def do_crawl(self, comic_case, download_request):
        cd = CrawlingDoer(comic_case, download_request, self.config)
        cc = cd.do_request()
        return cc


class CrawlingDoer:
    def __init__(self, comic_case, download_request, config):
        self.comic_case = comic_case
        self.config = config
        self.download_request = download_request

    def do_request(self):
        res = self.comic_case.to_raw()

        for comic in self.download_request.get_comics():
            if comic not in self.comic_case.to_raw():
                res[comic] = {}

        for comic in self.download_request.get_comics():
            ch_task = CrawlingTask('get_comic_home',
                                   comic, self.config)
            eu_task = CrawlingTask('get_episode_urls',
                                   ch_task.get_result(), self.config)

            for episode in eu_task.get_result().keys():

                # Check the condition below of the crawled episode
                # 1. in the comic case
                # 2. not in the request for downloading and request is not empty
                # if one of them is true, skip this episode.
                if self.comic_case.get(comic).get(episode).data != [] or \
                        (
                                self.download_request.get_episodes(comic) != {} and
                                episode not in self.download_request.get_episodes(comic)
                        ):
                    continue

                im_task = CrawlingTask('get_images',
                                       eu_task.get_result()[episode], self.config)
                res[comic][episode] = im_task.get_result()['image_urls']

        self.comic_case.from_raw(res)
        return self.comic_case


class CrawlingTask:
    def __init__(self, type_of_task, arg, config):
        self.task_name = "[{}]: {}".format(type_of_task, arg)
        self.worker_info = config['worker_info']

        if type_of_task == 'get_comic_home':
            self.code = generate_code_get_comic_home(config['code_dir_base'], arg)
        elif type_of_task == 'get_episode_urls':
            self.code = generate_code_get_episode_urls(config['code_dir_base'], arg)
        elif type_of_task == 'get_images':
            self.code = generate_code_get_images(config['code_dir_base'], arg)
        else:
            raise ValueError('Unsupported task type: ' + type_of_task)

        self.result = None

    def get_result(self, cache=True):
        if cache is False or self.result is None:
            self.execute()

        return self.result

    def execute(self):
        print('[Execute]' + self.task_name)
        if self.worker_info['type'] == 'direct':
            res = execute_code_directly(self.code)
        elif self.worker_info['type'] == 'worker':
            res = execute_code_with_worker(
                self.code, self.worker_info['url'])
        else:
            res = None

        self.result = res


def execute_code_directly(code):
    res = subprocess.run(
        ["python3"],
        stdout=subprocess.PIPE,
        input=bytes(code, 'utf-8')
    )

    return json.loads(res.stdout.decode('utf-8'))


def execute_code_with_worker(code, url):
    res = requests.get(
        url,
        {
            'code': urllib.parse.quote_plus(code),
        }
    )

    return json.loads(res.content)


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
