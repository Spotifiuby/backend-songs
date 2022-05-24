from fastapi import APIRouter, HTTPException, status, Header, Depends
from typing import Optional

from utils.utils import log_request_body, check_valid_song_id, verify_token
from utils.user import is_admin
from models.song import SongModel, CreateSongRequest, UpdateSongRequest
import service.song
from exceptions.song_exceptions import SongNotFound, SongNotOwnedByUser
from exceptions.user_exceptions import MissingUserId

song_routes = APIRouter()


def _verify_ownership(song_id, user_id):
    if not user_id:
        raise MissingUserId()
    if not service.song.is_owner(song_id, user_id) and not is_admin(user_id):
        raise SongNotOwnedByUser(song_id, user_id)


@song_routes.get("/songs", response_model=list[SongModel], tags=["Songs"], status_code=status.HTTP_200_OK)
async def get_songs(q: Optional[str] = None,
                    x_user_id: Optional[str] = Header(None),
                    x_api_key: Optional[str] = Header(None),
                    authorization: Optional[str] = Header(None)):
    verify_token(x_api_key)
    return service.song.find(q)


@song_routes.get("/songs/{song_id}", response_model=SongModel, tags=["Songs"], status_code=status.HTTP_200_OK)
async def get_song(song_id: str = Depends(check_valid_song_id),
                   x_user_id: Optional[str] = Header(None),
                   x_api_key: Optional[str] = Header(None),
                   authorization: Optional[str] = Header(None)):
    verify_token(x_api_key)
    song = service.song.get(song_id)
    if song is None:
        raise SongNotFound(song_id)
    return song


@song_routes.post("/songs", response_model=SongModel, tags=["Songs"], status_code=status.HTTP_201_CREATED)
async def create_song(song: CreateSongRequest,
                      x_user_id: Optional[str] = Header(None),
                      x_api_key: Optional[str] = Header(None),
                      authorization: Optional[str] = Header(None),
                      x_request_id: Optional[str] = Header(None)):
    log_request_body(x_request_id, song)
    verify_token(x_api_key)
    return service.song.create(song, x_user_id)


@song_routes.put("/songs/{song_id}", response_model=SongModel, tags=["Songs"])
async def update_song(song_id: str = Depends(check_valid_song_id), song: UpdateSongRequest = None,
                      x_user_id: Optional[str] = Header(None),
                      x_api_key: Optional[str] = Header(None),
                      authorization: Optional[str] = Header(None),
                      x_request_id: Optional[str] = Header(None)):
    log_request_body(x_request_id, song)
    verify_token(x_api_key)
    _verify_ownership(song_id, x_user_id)
    updated_song = service.song.update(song_id, song)
    if not updated_song:
        raise SongNotFound(song_id)

    return updated_song


@song_routes.delete("/songs/{song_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Songs"])
async def delete_song(song_id: str = Depends(check_valid_song_id),
                      x_user_id: Optional[str] = Header(None),
                      x_api_key: Optional[str] = Header(None),
                      authorization: Optional[str] = Header(None)):
    verify_token(x_api_key)
    _verify_ownership(song_id, x_user_id)
    r = service.song.delete(song_id)
    if not r:
        SongNotFound(song_id)


