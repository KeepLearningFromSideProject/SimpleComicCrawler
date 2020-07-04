"""
storage engine
"""

import json
from .dataclasses.comic_data_class import ComicCase

class StorageEngine:
    def __init__(self, config={'type': 'json', 'storage_path': '../db.json'}):
        self.storage_type = config['type']
        self.storage_path = config['storage_path']

        self.storage = get_storage_instance(
            storage_type = self.storage_type,
            storage_path = self.storage_path
        )

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

def get_storage_instance(storage_type, storage_path):
    if storage_type == 'json':
        return JsonStorageDriver(storage_path)
    else:
        raise NotImplemented(f'No such StorageDriver of type "{storage_type}"')
