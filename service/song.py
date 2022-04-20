from bson import ObjectId
import pymongo
from config.db import conn
from models.song import StatusEnum


def _song_entity(song) -> dict:
    song["id"] = str(song.pop("_id"))
    return song


def get_all():
    return [_song_entity(song) for song in conn.songs.find()]


def get(song_id: str):
    song = conn.songs.find_one({"_id": ObjectId(song_id)})
    if song:
        return _song_entity(song)

    return None


def create(song):
    song_dict = song.dict()
    song_dict["status"] = StatusEnum.not_uploaded
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
        {"$set": {"status": StatusEnum.active}},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return _song_entity(updated_song)
