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
            urllib.parse.urlencode({"k": pattern}, encoding='big5'))

    page = Soup(resp.content.decode('big5'), features="html.parser")
    rows = page.find_all('td', style="border-bottom:1px dotted #cccccc; line-height:18px; padding-left:5px ")

    results = []
    for row in rows:
        results.extend(row.find_all('a', href=True))

    ret = {}
    for r in results:
        title = r.find('font').getText()
        if title == pattern:
            return 'https://comicbus.com' + r['href']

    return None

if __name__== '__main__':
    comic_url = searchComic(comic_name)

    print(json.dumps(comic_url), end = '')

