"""
request handler
"""

from .storage_engine import StorageEngine
from .crawl_engine import CrawlEngine

from .dataclasses.comic_data_class import ComicCase
from .dataclasses.download_request import BasicDownloadRequest


class RequestHandler:
    """
    To handle the request from user.
    
    @param: crawler_config The config for crawler.
            For now, only one kind of config is available like:
            {"code_dir_base": "THE PATH TO THE scripts FOLDER"}
    @param: storage_config The config for storage.
            For now, only one kind of config is available like:
            {
                "type": "json",
                "storage_path": "THE PATH TO PLACE THE DB FILE"
            }
    """

    def __init__(self, crawler_config, storage_config):
        self.crawler_config = crawler_config
        self.crawler_engine = CrawlEngine(crawler_config)

        self.storage_config = storage_config
        self.storage_engine = StorageEngine(storage_config)

        self.result = ComicCase({})

    """
    To do the crawling task.

    @param: raw_request The request body in the format like:
            {
                // Means to download all the episode that is
                // available.
                "comic_name1": {}, 

                // Means to only download the episode having name
                // in "episode1" and "episode2".
                "comic_name2": { 
                    "episode1": [],
                    "episode2": []
                }
            }
    """

    def do(self, raw_request):
        dr = BasicDownloadRequest(raw_request)

        self.result = self.crawler_engine.do_crawl(
            comic_case=self.storage_engine.get_all(),
            download_request=dr
        )

    """
    To sync the download result to db.
    """

    def sync(self):
        self.storage_engine.save_all(
            comic_case=self.result
        )
