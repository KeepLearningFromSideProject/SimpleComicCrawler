import os
import sys
import json
import time
import signal
import shutil
import logging
import subprocess

from selenium import webdriver
from lib.request_handler import RequestHandler

import requests

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

CHROMELOG = 'tmp/chromedriver.log'

signal.signal(signal.SIGCHLD, signal.SIG_IGN)

def process(raw_request, code_base_dir, db, db_host, db_port, db_user, db_password):
    req_h = RequestHandler(
        crawler_config={
            'max_download': 1,
            'code_dir_base': code_base_dir,
            'worker_info': {
                'type': 'direct'
            }
        },
        storage_config={
            'type': 'mysql',
            'db': db,
            'db_host': db_host,
            'db_port': db_port,
            'db_user': db_user,
            'db_password': db_password
        }
    )

    req_h.do(raw_request)

def handler(event, context):
    with open(os.environ['req_file'], 'r') as src:
        raw_request = json.loads(src.read())

    LOGGER.info('Do process')
    proxy_process = subprocess.Popen(["bash", "/proxy_launch.sh"])

    process(
        raw_request=raw_request,
        code_base_dir='/var/task/SimpleComicCrawler/scripts',
        db=os.environ['db_name'],
        db_host=os.environ['db_host'],
        db_port=int(os.environ['db_port']),
        db_user=os.environ['db_user'],
        db_password=os.environ['db_pass'] 
    )
    
    os.system("killall -9 ssh")
    
    LOGGER.info('End process')

    if os.path.exists(CHROMELOG):
        with open(CHROMELOG, 'r') as logfile:
            log_str = logfile.read()
    else:
        log_str = ''

    return {
        'statusCode': 200,
        'body': log_str
    }

if __name__ == "__main__":
    print(handler([], []))

