# please add the target episode_url at the start of this code, example:
# episode_url = 'https://comicabc.com/online/new-13313.html?ch=85'

import os
import sys
import json
import subprocess

def doRequest(url):
    print(f"[Init Options]", file=sys.stderr)
    image_urls = []
    page_num = 0
    try:
        result = getImageSrc(url)
        isSuccess = result["status"] == "success"
        if isSuccess:
            image_urls = result["imageSrc"]
            page_num = result["totalAmout"]
        else:
            raise Exception("unable to fetch image src from get_images.js")

    except Exception as e:
        print(f"[Error] {e}", file=sys.stderr)

    return image_urls, page_num

def getImageSrc(url):

    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    res = subprocess.run(
        ["node", os.path.join(dir_path, 'scripts', 'nodejs_get_images', 'get_images.js'), url],
        stdout=subprocess.PIPE
    )
    return json.loads(res.stdout.decode('utf-8'))

if __name__== '__main__':
    image_urls, page_num = doRequest(episode_url)

    print(json.dumps({
        'page_num': page_num,
        'image_urls': image_urls
    }), end='')
