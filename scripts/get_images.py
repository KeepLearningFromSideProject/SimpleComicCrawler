# please add the target episode_url at the start of this code, example:
#episode_url = 'https://comicbus.live/online/a-9337.html?ch=315'

import os
import json
from selenium import webdriver

def isInLambda():
    return os.path.exists('/var/task')

def doRequest(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=socks5://localhost:8079')

    if isInLambda():
        chrome_options.binary_location = "/var/task/bin/headless-chromium"

    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--disable-application-cache')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--homedir=/tmp')

    try:
        if isInLambda():
            chromedriver = '/var/task/bin/chromedriver'
        else:
            chromedriver = 'chromedriver'

        driver = webdriver.Chrome(
            chromedriver,
            options=chrome_options,
            service_log_path='/tmp/chromedriver.log')

        driver.get(url)
        driver.implicitly_wait(10)

        page_num = int(driver.execute_script("return document.querySelector('#pageindex > option:last-child').value"))
        image_urls = []
        for i in range(1, page_num + 1):
            driver.get(f"{url}-{i}")
            image_urls.append(driver.execute_script("return document.getElementById('TheImg').src;"))
        driver.close()
    except Exception as e:
        print(e)
        image_urls = []
        page_num = 0

    return image_urls, page_num

if __name__== '__main__':
    image_urls, page_num = doRequest(episode_url)

    print(json.dumps({
        'page_num': page_num,
        'image_urls': image_urls
    }), end='')
