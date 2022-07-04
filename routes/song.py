from fastapi import APIRouter, status, Header, Depends, Response
from typing import Optional

from models.song import SongModel, CreateSongRequest, UpdateSongRequest
import service.song
import service.artist
from utils.utils import log_request_body, check_valid_song_id, verify_api_key, get_user_subscription
from utils.user import is_admin
from exceptions.song_exceptions import SongNotFound, SongNotOwnedByUser
from exceptions.user_exceptions import MissingUserId

song_routes = APIRouter()


def _verify_user_id(user_id):
    if not user_id:
        raise MissingUserId()
    return user_id


def _verify_ownership(song_id, user_id):
    if not service.song.is_owner(song_id, user_id) and not is_admin(user_id):
        raise SongNotOwnedByUser(song_id, user_id)


@song_routes.get("/songs", response_model=list[SongModel], tags=["Songs"], status_code=status.HTTP_200_OK)
async def get_songs(response: Response,
                    q: Optional[str] = None,
                    artist_id: Optional[str] = None,
                    x_user_id: Optional[str] = Header(None),
                    x_api_key: Optional[str] = Header(None),
                    authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    songs = service.song.find(q, artist_id, subscription_level=get_user_subscription(x_user_id))
    for song in songs:
        song['artists'] = [service.artist.get_name(artist_id) for artist_id in song['artists']]
    return songs


@song_routes.get("/songs/{song_id}", response_model=SongModel, tags=["Songs"], status_code=status.HTTP_200_OK)
async def get_song(response: Response,
                   song_id: str = Depends(check_valid_song_id),
                   x_user_id: Optional[str] = Header(None),
                   x_api_key: Optional[str] = Header(None),
                   authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    song = service.song.get(song_id)
    if song is None:
        raise SongNotFound(song_id)
    song['artists'] = [service.artist.get_name(artist_id) for artist_id in song['artists']]
    return song


@song_routes.post("/songs", response_model=SongModel, tags=["Songs"], status_code=status.HTTP_201_CREATED)
async def create_song(response: Response,
                      song: CreateSongRequest,
                      x_user_id: Optional[str] = Header(None),
                      x_api_key: Optional[str] = Header(None),
                      authorization: Optional[str] = Header(None),
                      x_request_id: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    log_request_body(x_request_id, song)
    verify_api_key(x_api_key)
    _verify_user_id(x_user_id)
    return service.song.create(song, x_user_id)


@song_routes.put("/songs/{song_id}", response_model=SongModel, tags=["Songs"])
async def update_song(response: Response,
                      song_id: str = Depends(check_valid_song_id),
                      song: UpdateSongRequest = None,
                      x_user_id: Optional[str] = Header(None),
                      x_api_key: Optional[str] = Header(None),
                      authorization: Optional[str] = Header(None),
                      x_request_id: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    log_request_body(x_request_id, song)
    verify_api_key(x_api_key)
    _verify_ownership(song_id, x_user_id)
    updated_song = service.song.update(song_id, song)
    if not updated_song:
        raise SongNotFound(song_id)

    return updated_song


@song_routes.delete("/songs/{song_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Songs"])
async def delete_song(response: Response,
                      song_id: str = Depends(check_valid_song_id),
                      x_user_id: Optional[str] = Header(None),
                      x_api_key: Optional[str] = Header(None),
                      authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    _verify_ownership(song_id, x_user_id)
    r = service.song.delete(song_id)
    if not r:
        SongNotFound(song_id)
