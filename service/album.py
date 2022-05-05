from bson import ObjectId
import pymongo
import datetime
from config.db import conn


def _album_entity(album) -> dict:
    album["id"] = str(album.pop("_id"))
    return album


def get_all():
    return [_album_entity(album) for album in conn.albums.find()]


def get(album_id: str):
    album = conn.albums.find_one({"_id": ObjectId(album_id)})
    if album:
        return _album_entity(album)

    return None


def create(album):
    album_dict = album.dict()
    album_dict["date_created"] = datetime.datetime.today()
    r = conn.albums.insert_one(album_dict)
    mongo_album = conn.albums.find_one({"_id": r.inserted_id})

    return _album_entity(mongo_album)


def add_song(album_id, song):
    updated_album = conn.albums.find_one_and_update(
        {"_id": ObjectId(album_id)},
        {"$push": {"songs": song}},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return _album_entity(updated_album)


def add_artist(album_id, artist):
    updated_album = conn.albums.find_one_and_update(
        {"_id": ObjectId(album_id)},
        {"$push": {"artists": artist}},
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
