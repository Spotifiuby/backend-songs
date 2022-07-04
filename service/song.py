from bson import ObjectId
import pymongo
import datetime

from config.db import conn
from models.song import StatusEnum
import service.artist
from exceptions.artist_exception import ArtistNotFoundForUser
from exceptions.song_exceptions import SongNotFound


def _song_entity(song) -> dict:
    if not song:
        return song
    song["id"] = str(song.pop("_id"))
    song['artists'] = [str(artist_id) for artist_id in song['artists']]
    return song


def _regex_query(field, q):
    return {field: {'$regex': q, '$options': 'i'}}


def find(q: str = None, artist_id: str | ObjectId = None, songs_ids: list = None, subscription_level: int = None):
    mongo_query = {}
    if q:
        fields = ['name', 'artists_names', 'genre']
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
                'artists_data',
                'artists_names',
                'subscription_level'
            ]
        }
    ]

    return [_song_entity(song) for song in conn.songs.aggregate(pipeline)]


def get(song_id: str):
    song = conn.songs.find_one({"_id": ObjectId(song_id)})
    return _song_entity(song)


def create(song, user_id):
    song_dict = song.dict()
    if "artists" not in song_dict or not song_dict["artists"]:
        song_dict["artists"] = []
    else:
        song_dict["artists"] = [ObjectId(a) for a in song_dict["artists"]]

    for artist_id in song_dict["artists"]:
        artist = service.artist.get(artist_id)
        if not artist:
            raise ArtistNotFoundForUser(user_id)

    if len(song_dict["artists"]) == 0:
        artist = service.artist.get(user_id=user_id)
        if not artist:
            raise ArtistNotFoundForUser(user_id)
        user_artist_id = ObjectId(artist['id'])
        song_dict["artists"].insert(0, user_artist_id)

    song_dict["status"] = StatusEnum.not_uploaded
    song_dict["date_created"] = datetime.datetime.today()
    song_dict["date_uploaded"] = None
    r = conn.songs.insert_one(song_dict)
    mongo_song = conn.songs.find_one({"_id": r.inserted_id})

    return _song_entity(mongo_song)


def is_owner(song_id, user_id):
    song = conn.songs.find_one({'_id': ObjectId(song_id)})
    if not song:
        raise SongNotFound(song_id)
    for artist_id in song['artists']:
        artist = service.artist.get(artist_id)
        if artist['user_id'] == user_id:
            return True
    return False


def update(song_id, song):
    to_update = {k: v for k, v in song.dict().items() if v is not None}
    if "artists" in to_update:
        to_update["artists"] = [ObjectId(artist_id) for artist_id in to_update["artists"]]
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
