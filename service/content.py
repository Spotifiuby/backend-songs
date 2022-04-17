from google.cloud import exceptions
from config.db import bucket


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
