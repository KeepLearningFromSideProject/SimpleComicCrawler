"""
storage engine
"""

import json
import requests
import pymysql

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


class MysqlDBDriver:
    def __init__(self, db, db_host, db_port, db_user, db_password):
        self.connection = pymysql.connect(
            db=db,
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password
        )

    def __del__(self):
        self.connection.close()

    def get_all(self):
        cursor = self.connection.cursor()
        raw = {}

        comic_records = get_all_comic(cursor)
        for comic_id, comic_name in comic_records:
            raw[comic_name] = {}
            episode_records = get_all_episodes(cursor, comic_id)
            for episode_id, episode_name in episode_records:
                raw[comic_name][episode_name] = get_all_comic_urls(cursor, episode_id)

        cursor.close()
        return raw

    def save_all(self, raw):
        cursor = self.connection.cursor()
        for comic_name in raw.keys():
            comic_id = select_comic_or_insert(cursor, comic_name)
            for episode_name in raw[comic_name].keys():
                episode_id = select_episode_or_insert(cursor, comic_id, episode_name)
                for image_url in raw[comic_name][episode_name]:
                    select_image_or_insert(cursor, comic_id, episode_id, image_url)

        self.connection.commit()
        cursor.close()


def get_storage_instance(storage_config):
    if storage_config["type"] == 'json':
        return JsonStorageDriver(storage_config["storage_path"])
    elif storage_config["type"] == 'fuse_db':
        return FuseDBDriver(storage_config['db_url'])
    elif storage_config["type"] == 'mysql':
        return MysqlDBDriver(
            storage_config['db'], storage_config['db_host'], storage_config['db_port'],
            storage_config['db_user'], storage_config['db_password']
        )
    else:
        raise NotImplemented(f'No such StorageDriver of type "{storage_config["type"]}"')


def select_comic_or_insert(cursor, comic_name):
    select_sql = "SELECT id FROM comics WHERE comic_name = %s"
    insert_sql = "INSERT INTO comics ( comic_name ) VALUES ( %s )"
    rec_len = cursor.execute(select_sql, comic_name)

    if rec_len > 0:
        return cursor.fetchone()[0]
    else:
        cursor.execute(insert_sql, comic_name)
        return cursor.lastrowid


def select_episode_or_insert(cursor, comic_id, episode_name):
    select_sql = "SELECT id FROM episodes WHERE comic_id = %s and episode_name = %s"
    insert_sql = "INSERT INTO episodes ( comic_id, episode_name ) VALUES ( %s, %s )"
    rec_len = cursor.execute(select_sql, (comic_id, episode_name))

    if rec_len > 0:
        return cursor.fetchone()[0]
    else:
        cursor.execute(insert_sql, (comic_id, episode_name))
        return cursor.lastrowid


def select_image_or_insert(cursor, comic_id, episode_id, image_url):
    select_sql = "SELECT id FROM images WHERE comic_id = %s and episode_id = %s and image_url = %s"
    insert_sql = "INSERT INTO images ( comic_id, episode_id, image_url ) VALUES ( %s, %s, %s )"
    rec_len = cursor.execute(select_sql, (comic_id, episode_id, image_url))

    if rec_len > 0:
        return cursor.fetchone()[0]
    else:
        cursor.execute(insert_sql, (comic_id, episode_id, image_url))
        return cursor.lastrowid

    return cursor.lastrowid


def get_all_comic(cursor):
    cursor.execute("SELECT * FROM comics")
    return cursor.fetchall()


def get_all_episodes(cursor, comic_id):
    cursor.execute("SELECT id, episode_name FROM episodes WHERE comic_id = %s", comic_id)
    return cursor.fetchall()


def get_all_comic_urls(cursor, episode_id):
    cursor.execute("SELECT image_url FROM images WHERE episode_id = %s", episode_id)
    return list(cursor.fetchall())
