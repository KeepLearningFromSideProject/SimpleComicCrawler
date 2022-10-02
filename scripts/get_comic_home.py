# please add the target comic_name at the start of this code, example:
# comic_name = b'\xe9\xa3\x9f\xe6\x88\x9f\xe4\xb9\x8b\xe9\x9d\x88'.decode(encoding='utf-8')

import requests
import urllib
import json

from bs4 import BeautifulSoup as Soup

def doRequest(url):
    return requests.get(url, cookies={'RI': '0'})

def searchComic(pattern):
    resp = doRequest(
            'https://comicbus.com/member/search.aspx?' + \
            urllib.parse.urlencode({"key": pattern}, encoding='utf-8'))

    page = Soup(resp.content.decode('utf-8'), features="html.parser")
    rows = page.find_all('div', class_="cat2_list text-center mb-4")

    results = []
    for row in rows:
        title = row.find('span').getText()
    
        if title == pattern:
            return row.find('a', href=True)['href']

    raise None


if __name__== '__main__':
    comic_url = searchComic(comic_name)

    print(json.dumps(comic_url), end = '')

