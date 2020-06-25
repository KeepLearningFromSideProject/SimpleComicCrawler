"""
crawl engine
"""

import os
import json
import subprocess


class CrawlingDoer:
    def __init__(self, comic_case, download_request, code_dir_base='../scripts'):
        self.comic_case = comic_case
        self.code_dir_base = code_dir_base
        self.download_request = download_request

    def do_request(self):
        res = self.comic_case.to_raw()

        res.update({
            comic: {}
            for comic in 
            self.download_request.get_comics()
        })

        for comic in self.download_request.get_comics():
            ch_task = CrawlingTask('get_comic_home',
                        comic, self.code_dir_base)
            eu_task = CrawlingTask('get_episode_urls',
                        ch_task.get_result(), self.code_dir_base)

            for episode in eu_task.get_result().keys():

                # Check the condition below of the crawled episode
                # 1. in the comic case
                # 2. not in the request for downlading and request is not empty
                # if one of them is true, skip this episode.
                if self.comic_case.get(comic).get(episode).data != [] or \
                    ( \
                        self.download_request.get_episodes(comic) != {} and \
                        episode not in self.download_request.get_episodes(comic) \
                    ):
                    continue

                im_task = CrawlingTask('get_images',
                        eu_task.get_result()[episode], self.code_dir_base)
                res[comic][episode] = im_task.get_result()['image_urls']

        self.comic_case.from_raw(res)
        return self.comic_case

class CrawlingTask:
    def __init__(self, type_of_task, arg, code_dir_base):
        self.task_name = "[{}]: {}".format(type_of_task, arg)

        if type_of_task == 'get_comic_home':
            self.code = generate_code_get_comic_home(code_dir_base, arg)
        elif type_of_task == 'get_episode_urls':
            self.code = generate_code_get_episode_urls(code_dir_base, arg)
        elif type_of_task == 'get_images':
            self.code = generate_code_get_images(code_dir_base, arg)
        else:
            raise ValueError('Unsupported task type: ' + type_of_task)

        self.result = None

    def get_result(self, cache=True):
        if cache == False or self.result == None:
            self.execute()

        return self.result

    def execute(self):
        print('[Execute]' + self.task_name)
        res = subprocess.run(
            ["python3"],
            stdout=subprocess.PIPE,
            input=bytes(self.code, 'utf-8')
        )

        self.result = json.loads(res.stdout.decode('utf-8'))

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
