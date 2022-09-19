#!/usr/bin/env python3
"""
A mysql runner to crawl comic

@argv[1]: the file path of request json
@argv[2]: the directory of crawling scripts
@argv[3]: db name
@argv[4]: db host
@argv[5]: db port
@argv[6]: db user
@argv[7]: db password
@argv[8]: the maximum number of episodes to download
"""

import sys
import json

from lib.request_handler import RequestHandler


def process(raw_request, code_base_dir, db, db_host, db_port, db_user, db_password, max_download):
    req_h = RequestHandler(
        crawler_config={
            'max_download': max_download,
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


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as src:
        raw_request = json.loads(src.read())

    process(
        raw_request=raw_request,
        code_base_dir=sys.argv[2],
        db=sys.argv[3],
        db_host=sys.argv[4],
        db_port=int(sys.argv[5]),
        db_user=sys.argv[6],
        db_password=sys.argv[7],
        max_download=int(sys.argv[8])
    )
