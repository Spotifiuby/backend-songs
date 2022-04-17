from google.cloud import storage, exceptions
from config.db import BUCKET


def get_song_content(song_id: str):
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET)
    blob = bucket.blob(f"{song_id}/{song_id}.mp3")
    try:
        contents = blob.download_as_string()
    except exceptions.NotFound:
        return None
    return contents
