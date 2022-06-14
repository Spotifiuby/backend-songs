from google.cloud import exceptions

import service.artist
import service.song
from config.db import bucket
from config.db import conn
from exceptions.content_exceptions import ContentForbidden
from exceptions.song_exceptions import SongNotFound
from utils.user import is_admin


def get_song_content(song_id: str):
    blob = bucket.blob(f"{song_id}/{song_id}.mp3")
    try:
        contents = blob.download_as_string()
    except exceptions.NotFound:
        return None
    return contents


def upload_song_content(song_id: str, contents):
    blob = bucket.blob(f"{song_id}/{song_id}.mp3")
    blob.upload_from_string(contents)


def verify_download(user_id: str, song_id: str, authorization):
    if is_admin(user_id, authorization):
        return

    song = service.song.get(song_id)
    if not song:
        raise SongNotFound(song_id)

    artists_max_level = 0
    for artist_id in song['artists']:
        artist = service.artist.get(artist_id)
        if artist['user_id'] == user_id:
            return
        if "subscription_level" in artist:
            artists_max_level = max(artists_max_level, artist["subscription_level"])
    if artists_max_level == 0:
        return

    user_subscription_level = 0
    subscription = conn.subscriptions.find_one({"user_id": user_id})
    if subscription:
        user_subscription_level = subscription["subscription_type_level"]

    if user_subscription_level >= artists_max_level:
        return

    raise ContentForbidden(song_id, user_id)
