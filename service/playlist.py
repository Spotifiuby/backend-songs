from bson import ObjectId
import pymongo
import datetime
from config.db import conn


def _playlist_entity(playlist) -> dict:
    if not playlist:
        return playlist
    playlist["id"] = str(playlist.pop("_id"))
    return playlist


def _regex_query(field, q):
    return {field: {'$regex': q, '$options': 'i'}}


def find(q):
    if not q:
        mongo_query = {}
    else:
        fields = ['name', 'owner']
        mongo_query = {'$or': [_regex_query(field, q) for field in fields]}
    return [_playlist_entity(song) for song in conn.playlists.find(mongo_query)]


def get(playlist_id: str):
    playlist = conn.playlists.find_one({"_id": ObjectId(playlist_id)})
    return _playlist_entity(playlist)


def create(playlist):
    playlist_dict = playlist.dict()
    playlist_dict["date_created"] = datetime.datetime.today()
    r = conn.playlists.insert_one(playlist_dict)
    mongo_playlist = conn.playlists.find_one({"_id": r.inserted_id})

    return _playlist_entity(mongo_playlist)


def add_song(playlist_id, song):
    updated_playlist = conn.playlists.find_one_and_update(
        {"_id": ObjectId(playlist_id)},
        {"$push": {"songs": song}},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return _playlist_entity(updated_playlist)


def update(playlist_id, playlist):
    to_update = {k: v for k, v in playlist.dict().items() if v is not None}
    updated_playlist = conn.playlists.find_one_and_update(
        {"_id": ObjectId(playlist_id)},
        {"$set": to_update},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return _playlist_entity(updated_playlist)


def delete(playlist_id):
    r = conn.playlists.delete_one({"_id": ObjectId(playlist_id)})
    return r.deleted_count > 0
