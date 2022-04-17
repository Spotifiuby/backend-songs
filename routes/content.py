from fastapi import APIRouter, Response
from google.cloud import storage

content_routes = APIRouter()


@content_routes.get("/songs/{song_id}/content", response_class=Response, tags=["Content"])
def get_content():
    storage_client = storage.Client()
    bucket = storage_client.bucket("spotifiuby-3c9fe.appspot.com")
    blob = bucket.blob("test/test.mp3")
    contents = blob.download_as_string()
    return Response(media_type="audio/mpeg3", content=contents)
