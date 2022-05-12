from bson import ObjectId
import pymongo
import datetime
from config.db import conn
from models.song import StatusEnum


def _song_entity(song) -> dict:
    if not song:
        return song
    song["id"] = str(song.pop("_id"))
    return song


def _regex_query(field, q):
    return {field: {'$regex': q, '$options': 'i'}}


def find(q):
    if not q:
        mongo_query = {}
    else:
        fields = ['name', 'artists', 'genre']
        mongo_query = {'$or': [_regex_query(field, q) for field in fields]}
    return [_song_entity(song) for song in conn.songs.find(mongo_query)]


def get(song_id: str):
    song = conn.songs.find_one({"_id": ObjectId(song_id)})
    return _song_entity(song)


def create(song):
    song_dict = song.dict()
    song_dict["status"] = StatusEnum.not_uploaded
    song_dict["date_created"] = datetime.datetime.today()
    song_dict["date_uploaded"] = None
    r = conn.songs.insert_one(song_dict)
    mongo_song = conn.songs.find_one({"_id": r.inserted_id})

    return _song_entity(mongo_song)


def update(song_id, song):
    to_update = {k: v for k, v in song.dict().items() if v is not None}
    updated_song = conn.songs.find_one_and_update(
        {"_id": ObjectId(song_id)},
        {"$set": to_update},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return _song_entity(updated_song)


def delete(song_id):
    r = conn.songs.delete_one({"_id": ObjectId(song_id)})
    return r.deleted_count > 0


def activate_song(song_id):
    updated_song = conn.songs.find_one_and_update(
        {"_id": ObjectId(song_id)},
        {
            "$set": {
                "status": StatusEnum.active,
                "date_uploaded": datetime.datetime.today()
            }
        },
        return_document=pymongo.ReturnDocument.AFTER
    )
    return _song_entity(updated_song)
