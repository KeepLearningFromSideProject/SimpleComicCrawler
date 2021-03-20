# please add the target episode_url at the start of this code, example:
#episode_url = 'https://comicbus.live/online/a-9337.html?ch=315'

import json
from selenium import webdriver

def doRequest(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--proxy-server=socks5://localhost:8080')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.implicitly_wait(10)

    page_num = int(driver.execute_script("return document.querySelector('#pageindex > option:last-child').value"))
    image_urls = []
    for i in range(1, page_num + 1):
        driver.get(f"{url}-{i}")
        image_urls.append(driver.execute_script("return document.getElementById('TheImg').src;"))

    driver.close()

    return image_urls, page_num

if __name__== '__main__':
    image_urls, page_num = doRequest(episode_url)

    print(json.dumps({
        'page_num': page_num,
        'image_urls': image_urls
    }), end = '')
