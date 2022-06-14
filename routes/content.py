from fastapi import APIRouter, Response, UploadFile, status, Depends, Header
from typing import Optional

from exceptions.content_exceptions import ContentNotFound
from service.content import get_song_content, upload_song_content, verify_download
import service.song
from utils.utils import validate_song, verify_api_key

content_routes = APIRouter()


@content_routes.get("/songs/{song_id}/content", response_class=Response, tags=["Content"])
async def get_content(response: Response,
                      song_id: str = Depends(validate_song),
                      x_user_id: Optional[str] = Header(None),
                      x_api_key: Optional[str] = Header(None),
                      authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    verify_download(x_user_id, song_id, authorization)

    contents = get_song_content(song_id)
    if contents:
        return Response(media_type="audio/mpeg", content=contents)
    else:
        raise ContentNotFound(song_id)


@content_routes.post("/songs/{song_id}/content", response_class=Response, tags=["Content"])
async def post_content(response: Response,
                       song_id: str = Depends(validate_song),
                       file: UploadFile = None,
                       x_user_id: Optional[str] = Header(None),
                       x_api_key: Optional[str] = Header(None),
                       authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    upload_song_content(song_id, await file.read())
    service.song.activate_song(song_id)
    return Response(status_code=status.HTTP_201_CREATED)
