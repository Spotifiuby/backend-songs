from fastapi import APIRouter, Response, UploadFile, status, Depends
from exceptions.content_exceptions import ContentNotFound
from service.content import get_song_content, upload_song_content
import service.song
from utils.utils import validate_song

content_routes = APIRouter()


@content_routes.get("/songs/{song_id}/content", response_class=Response, tags=["Content"])
async def get_content(song_id: str = Depends(validate_song)):
    contents = get_song_content(song_id)
    if contents:
        return Response(media_type="audio/mpeg", content=contents)
    else:
        raise ContentNotFound(song_id)


@content_routes.post("/songs/{song_id}/content", response_class=Response, tags=["Content"])
async def post_content(song_id: str = Depends(validate_song), file: UploadFile = None):
    upload_song_content(song_id, await file.read())
    service.song.activate_song(song_id)
    return Response(status_code=status.HTTP_201_CREATED)
