from bson import ObjectId
import pymongo
import datetime

from config.db import conn
import service.song


def _album_entity(album) -> dict:
    if not album:
        return album
    album['id'] = str(album.pop('_id'))
    album['artists'] = [str(artist_id) for artist_id in album['artists']]
    return album


def _regex_query(field, q):
    return {field: {'$regex': q, '$options': 'i'}}


def find(q, artist_id):
    mongo_query = {}
    if q:
        fields = ['name']
        mongo_query = {'$or': [_regex_query(field, q) for field in fields]}
    if artist_id:
        mongo_query['artists'] = ObjectId(artist_id)
    return [_album_entity(song) for song in conn.albums.find(mongo_query)]


def get(album_id: str):
    album = conn.albums.find_one({"_id": ObjectId(album_id)})
    if album:
        return _album_entity(album)

    return None


def get_songs(album_id: str):
    album = conn.albums.find_one({"_id": ObjectId(album_id)})
    songs = [service.song.get(song_id) for song_id in album['songs']]
    return songs


def create(album):
    album_dict = album.dict()
    album_dict["date_created"] = datetime.datetime.today()
    album_dict["artists"] = [ObjectId(a) for a in album_dict["artists"]]
    r = conn.albums.insert_one(album_dict)
    mongo_album = conn.albums.find_one({"_id": r.inserted_id})

    return _album_entity(mongo_album)


def add_song(album_id, song_id):
    updated_album = conn.albums.find_one_and_update(
        {"_id": ObjectId(album_id)},
        {"$push": {"songs": song_id}},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return _album_entity(updated_album)


def add_artist(album_id, artist_id):
    updated_album = conn.albums.find_one_and_update(
        {"_id": ObjectId(album_id)},
        {"$push": {"artists": artist_id}},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return _album_entity(updated_album)


def update(album_id, album):
    to_update = {k: v for k, v in album.dict().items() if v is not None}
    updated_album = conn.albums.find_one_and_update(
        {"_id": ObjectId(album_id)},
        {"$set": to_update},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return _album_entity(updated_album)


def delete(album_id):
    r = conn.albums.delete_one({"_id": ObjectId(album_id)})
    return r.deleted_count > 0
