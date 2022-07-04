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
    album['songs'] = [str(song_id) for song_id in album['songs']]
    return album


def _regex_query(field, q):
    return {field: {'$regex': q, '$options': 'i'}}


def find(q: str = None, artist_id: str | ObjectId = None, songs_ids: list = None, subscription_level: int = None):
    mongo_query = {}
    if q:
        fields = ['name', 'artists_names']
        mongo_query = {'$or': [_regex_query(field, q) for field in fields]}
    if artist_id:
        mongo_query['artists'] = ObjectId(artist_id)
    if subscription_level is not None:
        mongo_query['subscription_level'] = {'$lte': subscription_level}
    if songs_ids:
        mongo_query['_id'] = {'$in': [ObjectId(song_id) for song_id in songs_ids]}

    pipeline = [
        {
            '$lookup': {
                'from': 'artists',
                'localField': 'artists',
                'foreignField': '_id',
                'as': 'artists_data'
            }
        }, {
            '$addFields': {
                'subscription_level': {
                    '$max': '$artists_data.subscription_level'
                },
                'artists_names': '$artists_data.name'
            }
        }, {
            '$match': mongo_query
        }, {
            '$unset': [
                'artists_data', 'artists_names', 'subscription_level'
            ]
        }
    ]

    return [_album_entity(song) for song in conn.albums.aggregate(pipeline)]


def get(album_id: str):
    album = conn.albums.find_one({"_id": ObjectId(album_id)})
    if album:
        return _album_entity(album)

    return None


def get_songs(album_id: str, subscription_level: int):
    album = conn.albums.find_one({"_id": ObjectId(album_id)})
    songs = service.song.find(songs_ids=album['songs'], subscription_level=subscription_level)
    return songs


def create(album):
    album_dict = album.dict()
    album_dict["date_created"] = datetime.datetime.today()
    album_dict["songs"] = [ObjectId(song_id) for song_id in album_dict["songs"]]
    album_dict["artists"] = [ObjectId(a) for a in album_dict["artists"]]
    if "cover" not in album_dict:
        album_dict["cover"] = None
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
    if "artists" in to_update:
        to_update["artists"] = [ObjectId(artist_id) for artist_id in to_update["artists"]]
    if "songs" in to_update:
        to_update["songs"] = [ObjectId(song_id) for song_id in to_update["songs"]]
    updated_album = conn.albums.find_one_and_update(
        {"_id": ObjectId(album_id)},
        {"$set": to_update},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return _album_entity(updated_album)


def delete(album_id):
    r = conn.albums.delete_one({"_id": ObjectId(album_id)})
    return r.deleted_count > 0
