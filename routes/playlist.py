from fastapi import APIRouter, HTTPException, status, Header
from bson import ObjectId
from typing import Optional

from models.playlist import PlaylistModel, CreatePlaylistRequest, UpdatePlaylistRequest
import service.playlist
from utils.utils import log_request_body, validate_song, verify_api_key, check_valid_playlist_id

playlist_routes = APIRouter()


@playlist_routes.get("/playlists", response_model=list[PlaylistModel], tags=["Playlists"], status_code=status.HTTP_200_OK)
async def get_playlists(q: Optional[str] = None,
                        x_user_id: Optional[str] = Header(None),
                        x_api_key: Optional[str] = Header(None),
                        authorization: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    return service.playlist.find(q)


@playlist_routes.get("/playlists/{playlist_id}", response_model=PlaylistModel, tags=["Playlists"], status_code=status.HTTP_200_OK)
async def get_playlist(playlist_id: str,
                       x_user_id: Optional[str] = Header(None),
                       x_api_key: Optional[str] = Header(None),
                       authorization: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    check_valid_playlist_id(playlist_id)
    playlist = service.playlist.get(playlist_id)
    if playlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist {playlist_id} not found")

    return playlist


@playlist_routes.post("/playlists", response_model=PlaylistModel, tags=["Playlists"], status_code=status.HTTP_201_CREATED)
async def create_playlist(playlist: CreatePlaylistRequest,
                          x_request_id: Optional[str] = Header(None),
                          x_user_id: Optional[str] = Header(None),
                          x_api_key: Optional[str] = Header(None),
                          authorization: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    for song in playlist.songs:
        validate_song(song)
    log_request_body(x_request_id, playlist)
    return service.playlist.create(playlist)


@playlist_routes.put("/playlists/{playlist_id}/songs", response_model=PlaylistModel, tags=["Playlists"])
async def add_song(playlist_id: str, song: str,
                   x_request_id: Optional[str] = Header(None),
                   x_user_id: Optional[str] = Header(None),
                   x_api_key: Optional[str] = Header(None),
                   authorization: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    check_valid_playlist_id(playlist_id)
    validate_song(song)
    log_request_body(x_request_id, {"song": song})

    updated_playlist = service.playlist.add_song(playlist_id, song)
    if not updated_playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist {playlist_id} not found")

    return updated_playlist


@playlist_routes.put("/playlists/{playlist_id}", response_model=PlaylistModel, tags=["Playlists"])
async def update_playlist(playlist_id: str, playlist: UpdatePlaylistRequest,
                          x_request_id: Optional[str] = Header(None),
                          x_user_id: Optional[str] = Header(None),
                          x_api_key: Optional[str] = Header(None),
                          authorization: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    check_valid_playlist_id(playlist_id)
    if playlist.songs:
        for song in playlist.songs:
            validate_song(song)
    log_request_body(x_request_id, playlist)

    updated_playlist = service.playlist.update(playlist_id, playlist)
    if not updated_playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist {playlist_id} not found")

    return updated_playlist


@playlist_routes.delete("/playlists/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Playlists"])
async def delete_playlist(playlist_id: str,
                          x_user_id: Optional[str] = Header(None),
                          x_api_key: Optional[str] = Header(None),
                          authorization: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    check_valid_playlist_id(playlist_id)
    r = service.playlist.delete(playlist_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist {playlist_id} not found")
