#!/usr/bin/env python3
"""
A basic runner to crawl comic

@argv[1]: the file path of request json
@argv[2]: the directory of crawling scripts
@argv[3]: the path of the database file
"""

import sys
import json

from lib.request_handler import RequestHandler


def process(raw_request, code_base_dir, storage_path):
    req_h = RequestHandler(
        crawler_config={
            'code_dir_base': code_base_dir,
            'worker_info': {
                'type': 'direct'
            }
        },
        storage_config={
            'type': 'json',
            'storage_path': storage_path}
    )

    req_h.do(raw_request)


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as src:
        raw_request = json.loads(src.read())

    process(
        raw_request=raw_request,
        code_base_dir=sys.argv[2],
        storage_path=sys.argv[3]
    )
