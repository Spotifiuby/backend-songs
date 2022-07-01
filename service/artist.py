from bson import ObjectId
import pymongo
import datetime

from config.db import conn
from utils.utils import check_valid_artist_id


def _artist_entity(artist) -> dict:
    if not artist:
        return artist
    artist["id"] = str(artist.pop("_id"))
    return artist


def _regex_query(field, q):
    return {field: {'$regex': q, '$options': 'i'}}


def find(q):
    if not q:
        mongo_query = {}
    else:
        fields = ['name']
        mongo_query = {'$or': [_regex_query(field, q) for field in fields]}
    return [_artist_entity(artist) for artist in conn.artists.find(mongo_query)]


def get(artist_id: str = None, user_id: str = None):
    artist = None
    if artist_id:
        check_valid_artist_id(artist_id)
        artist = conn.artists.find_one({"_id": ObjectId(artist_id)})
    elif user_id:
        artist = conn.artists.find_one({"user_id": user_id})
    return _artist_entity(artist)


def get_name(artist_id: str):
    artist = conn.artists.find_one({"_id": ObjectId(artist_id)})
    return artist['name']


def create(name, subscription_level, user_id):
    artist_dict = dict()
    artist_dict['name'] = name
    artist_dict['user_id'] = user_id
    artist_dict['subscription_level'] = subscription_level if subscription_level else 0
    artist_dict['date_created'] = datetime.datetime.today()
    r = conn.artists.insert_one(artist_dict)
    mongo_artist = conn.artists.find_one({'_id': r.inserted_id})

    return _artist_entity(mongo_artist)


def update(artist_id, name=None, subscription_level=None):
    artist = {}
    if name:
        artist['name'] = name
    if subscription_level:
        artist['subscription_level'] = subscription_level
    updated_artist = conn.artists.find_one_and_update(
        {"_id": ObjectId(artist_id)},
        {"$set": artist},
        return_document=pymongo.ReturnDocument.AFTER
    )
    return _artist_entity(updated_artist)


def delete(artist_id):
    r = conn.artists.delete_one({"_id": ObjectId(artist_id)})
    return r.deleted_count > 0
