#!/usr/bin/env python3
"""
A basic runner to crawl comic with the usage of fuse storage driver

@argv[1]: the file path of request json
@argv[2]: the directory of crawling scripts
@argv[3]: the url of fuse db
"""

import sys
import json

from lib.request_handler import RequestHandler


def process(raw_request, code_base_dir, db_url):
    req_h = RequestHandler(
        crawler_config={
            'max_download': -1,
            'code_dir_base': code_base_dir,
            'worker_info': {
                'type': 'direct'
            }
        },
        storage_config={
            'type': 'fuse_db',
            'db_url': db_url}
    )

    req_h.do(raw_request)


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as src:
        raw_request = json.loads(src.read())

    process(
        raw_request=raw_request,
        code_base_dir=sys.argv[2],
        db_url=sys.argv[3]
    )
