from bson import ObjectId
import pymongo
import datetime

from config.db import conn
from exceptions.playlist_exceptions import PlaylistNotFound
import service.song


def _playlist_entity(playlist) -> dict:
    if not playlist:
        return playlist
    playlist["id"] = str(playlist.pop("_id"))
    playlist["songs"] = [str(song_id) for song_id in playlist["songs"]]
    return playlist


def _regex_query(field, q):
    return {field: {'$regex': q, '$options': 'i'}}


def is_owner(playlist_id, user_id):
    playlist = conn.playlists.find_one({'_id': ObjectId(playlist_id)})
    if not playlist:
        raise PlaylistNotFound(playlist_id)
    return playlist['owner'] == user_id


def find(q):
    if not q:
        mongo_query = {}
    else:
        fields = ['name', 'owner']
        mongo_query = {'$or': [_regex_query(field, q) for field in fields]}
    return [_playlist_entity(playlist) for playlist in conn.playlists.find(mongo_query)]


def get(playlist_id: str):
    playlist = conn.playlists.find_one({"_id": ObjectId(playlist_id)})
    return _playlist_entity(playlist)


def get_songs(playlist_id: str, subscription_level: int):
    playlist = conn.playlists.find_one({"_id": ObjectId(playlist_id)})
    songs = service.song.find(songs_ids=playlist['songs'], subscription_level=subscription_level)
    return songs


def create(playlist, owner):
    playlist_dict = playlist.dict()
    playlist_dict["date_created"] = datetime.datetime.today()
    playlist_dict["owner"] = owner
    playlist_dict["songs"] = [ObjectId(song_id) for song_id in playlist_dict["songs"]]
    if "cover" not in playlist_dict:
        playlist_dict["cover"] = None
    r = conn.playlists.insert_one(playlist_dict)
    mongo_playlist = conn.playlists.find_one({"_id": r.inserted_id})

    return _playlist_entity(mongo_playlist)


def add_songs(playlist_id, songs):
    updated_playlist = conn.playlists.find_one_and_update(
        {"_id": ObjectId(playlist_id)},
        {"$push": {"songs": {"$each": songs}}},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return _playlist_entity(updated_playlist)


def delete_song(playlist_id, song_id):
    updated_playlist = conn.playlists.find_one_and_update(
        {"_id": ObjectId(playlist_id)},
        {"$pull": {"songs": song_id}},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return _playlist_entity(updated_playlist)


def update(playlist_id, playlist):
    to_update = {k: v for k, v in playlist.dict().items() if v is not None}
    if "songs" in to_update:
        to_update["songs"] = [ObjectId(song_id) for song_id in to_update["songs"]]
    updated_playlist = conn.playlists.find_one_and_update(
        {"_id": ObjectId(playlist_id)},
        {"$set": to_update},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return _playlist_entity(updated_playlist)


def delete(playlist_id):
    r = conn.playlists.delete_one({"_id": ObjectId(playlist_id)})
    return r.deleted_count > 0
