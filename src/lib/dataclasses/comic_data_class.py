"""
<I>comic data
"""

import json
from abc import ABC, abstractmethod

class ComicData(ABC):
    def __init__(self, raw_data={}):
        self.name = ""
        self.from_raw(raw_data)

    @abstractmethod
    def to_raw(self):
        pass

    @abstractmethod
    def from_raw(self):
        pass

    @abstractmethod
    def to_storage(self):
        pass

    @abstractmethod
    def from_storage(self):
        pass

class Image(ComicData):
    def to_raw(self):
        return self.data

    def from_raw(self, raw_data):
        self.data = raw_data

    def to_storage(self):
        with open('image_vfs.json', 'w') as dst:
            dst.write(json.dumps(self.data))

    def from_storage(self):
        with open('image_vfs.json', 'r') as src:
            self.data = json.loads(src.read())

class Episode(ComicData):
    def to_raw(self):
        result = []
        for image in self.data:
            result.append(image.to_raw())

        return {self.name: result}

    def from_raw(self, raw_data):
        self.name = list(raw_data.keys())[0]
        self.data = []
        
        raw_images = raw_data[self.name]
        for image_url in raw_images:
            self.data.append(Image(image_url))

    def to_storage(self):
        with open('Episode_vfs.json', 'w') as dst:
            dst.write(json.dumps(self.to_raw()))

    def from_storage(self):
        with open('Episode_vfs.json', 'r') as src:
            self.from_raw(json.loads(src.read()))

class Comic(ComicData):
    def to_raw(self):
        result = {}
        for episode in self.data:
            result.update(episode.to_raw())

        return {self.name: result}

    def from_raw(self, raw_data):
        self.name = list(raw_data.keys())[0]
        self.data = []

        raw_episodes = raw_data[self.name]
        for e_name, e_data in raw_episodes.items():
            self.data.append(Episode({e_name: e_data}))
        
    def to_storage(self):
        with open('Comic_vfs.json', 'w') as dst:
            dst.write(json.dumps(self.to_raw()))

    def from_storage(self):
        with open('Comic_vfs.json', 'r') as src:
            self.from_raw(json.loads(src.read()))

class ComicCase(ComicData):
    def to_raw(self):
        result = {}
        for comic in self.data:
            result.update(comic.to_raw())

        return result

    def from_raw(self, raw_data):
        self.data = []
        for c_name, c_data in raw_data.items():
            self.data.append(Comic({c_name: c_data}))

    def to_storage(self):
        with open('ComicCase_vfs.json', 'w') as dst:
            dst.write(json.dumps(self.to_raw()))

    def from_storage(self):
        with open('ComicCase_vfs.json', 'r') as src:
            self.from_raw(json.loads(src.read()))

