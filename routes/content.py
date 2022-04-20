from fastapi import APIRouter, Response, UploadFile, status
from exceptions.content_exceptions import ContentNotFound
from exceptions.song_exceptions import SongNotFound, SongNotAvailable
from models.song import SongModel
from service.content import get_song_content, upload_song_content
import service.song

content_routes = APIRouter()


def _check_valid_song(song: dict):
    return SongModel.is_active(song)


def _get_song_and_validate(song_id: str):
    song = service.song.get(song_id)
    if not song:
        raise SongNotFound(song_id)
    if not _check_valid_song(song):
        raise SongNotAvailable(song_id)


@content_routes.get("/songs/{song_id}/content", response_class=Response, tags=["Content"])
async def get_content(song_id: str):
    _get_song_and_validate(song_id)

    contents = get_song_content(song_id)
    if contents:
        return Response(media_type="audio/mpeg", content=contents)
    else:
        raise ContentNotFound(song_id)


@content_routes.post("/songs/{song_id}/content", response_class=Response, tags=["Content"])
async def post_content(song_id: str, file: UploadFile):
    _get_song_and_validate(song_id)

    upload_song_content(song_id, await file.read())
    service.song.activate_song(song_id)
    return Response(status_code=status.HTTP_201_CREATED)
