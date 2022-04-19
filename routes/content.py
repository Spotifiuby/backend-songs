from fastapi import APIRouter, Response, HTTPException, UploadFile
from service.content import get_song_content, upload_song_content
import service.song
from http import HTTPStatus

content_routes = APIRouter()


def _check_valid_song(song):
    # return song and "status" in song and song["status"] == "active"
    return True


@content_routes.get("/songs/{song_id}/content", response_class=Response, tags=["Content"])
async def get_content(song_id: str):
    # song = service.song.get(song_id)
    # if not _check_valid_song(song):
    #   raise HTTPException(status_code=400, detail=f"Song not available {song_id}")

    contents = get_song_content(song_id)
    if contents:
        return Response(media_type="audio/mpeg", content=contents)
    else:
        raise HTTPException(status_code=404, detail=f"Content not found for song {song_id}")


@content_routes.post("/songs/{song_id}/content", response_class=Response, tags=["Content"])
async def post_content(song_id: str, file: UploadFile):
    # song = service.song.get(song_id)
    # if not _check_valid_song(song):
    #     raise HTTPException(status_code=400, detail=f"Song not available {song_id}")

    upload_song_content(song_id, await file.read())
    return Response(status_code=HTTPStatus.CREATED)
