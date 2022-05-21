from fastapi import APIRouter, HTTPException, status, Header, Depends
from typing import Optional

from utils.utils import log_request_body, check_valid_song_id, verify_token
from models.song import SongModel, CreateSongRequest, UpdateSongRequest
import service.song

song_routes = APIRouter()


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Song {song_id} not found")

    return song


@song_routes.post("/songs", response_model=SongModel, tags=["Songs"], status_code=status.HTTP_201_CREATED)
async def create_song(song: CreateSongRequest,
                      x_user_id: Optional[str] = Header(None),
                      x_api_key: Optional[str] = Header(None),
                      authorization: Optional[str] = Header(None),
                      x_request_id: Optional[str] = Header(None)):
    log_request_body(x_request_id, song)
    verify_token(x_api_key)
    return service.song.create(song)


@song_routes.put("/songs/{song_id}", response_model=SongModel, tags=["Songs"])
async def update_song(song_id: str = Depends(check_valid_song_id), song: UpdateSongRequest = None,
                      x_user_id: Optional[str] = Header(None),
                      x_api_key: Optional[str] = Header(None),
                      authorization: Optional[str] = Header(None),
                      x_request_id: Optional[str] = Header(None)):
    log_request_body(x_request_id, song)
    verify_token(x_api_key)
    # if not service.song.is_owner(song_id, x_user_id):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
    #                         detail=f"The owner of song {song_id} is not {x_user_id}")
    updated_song = service.song.update(song_id, song)
    if not updated_song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Song {song_id} not found")

    return updated_song


@song_routes.delete("/songs/{song_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Songs"])
async def delete_song(song_id: str = Depends(check_valid_song_id),
                      x_user_id: Optional[str] = Header(None),
                      x_api_key: Optional[str] = Header(None),
                      authorization: Optional[str] = Header(None)):
    verify_token(x_api_key)
    r = service.song.delete(song_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Song {song_id} not found")


