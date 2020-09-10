"""
download order
"""


class BasicDownloadRequest:
    def __init__(self, raw_data={}):
        self.from_raw(raw_data)

    def from_raw(self, raw_data):
        self.request = raw_data

    def to_raw(self):
        return self.request

    def get_comics(self):
        return list(self.request.keys())

    def get_episodes(self, comic_name):
        return list(self.request[comic_name].keys())
