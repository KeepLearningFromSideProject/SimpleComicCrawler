"""
storage engine
"""

import json
import requests
from .dataclasses.comic_data_class import ComicCase


class StorageEngine:
    def __init__(self, config={'type': 'json', 'storage_path': '../db.json'}):
        self.storage = get_storage_instance(config)

    def get_all(self):
        raw = self.storage.get_all()
        return ComicCase(raw)

    def save_all(self, comic_case):
        raw = comic_case.to_raw()
        self.storage.save_all(raw)


class JsonStorageDriver:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_all(self):
        with open(self.file_path, 'r') as src:
            return json.loads(src.read())

    def save_all(self, raw):
        with open(self.file_path, 'w') as dst:
            dst.write(json.dumps(raw, indent=4))


class FuseDBDriver:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_all(self):
        all_raw = {}
        comics = requests.get(self.db_url + "/list").json()['data']
        for comic in comics:
            all_raw[comic] = {}
            episodes = requests.get(self.db_url + f"/list/{comic}").json()['data']
            for episode in episodes:
                all_raw[comic][episode] = [
                    *requests.get(self.db_url + f"/list/{comic}/{episode}").json()['data']
                ]

        return all_raw

    def save_all(self, raw):
        db_raw = self.get_all()
        new_raw = {}

        for comic in raw:
            new_raw[comic] = {}
            for episode in raw[comic]:
                if episode not in db_raw[comic]:
                    new_raw[comic][episode] = raw[comic][episode]

        requests.post(
            self.db_url + '/add', json=raw
        )


def get_storage_instance(storage_config):
    if storage_config["type"] == 'json':
        return JsonStorageDriver(storage_config["storage_path"])
    elif storage_config["type"] == 'fuse_db':
        return FuseDBDriver(storage_config['db_url'])
    else:
        raise NotImplemented(f'No such StorageDriver of type "{storage_config["type"]}"')
