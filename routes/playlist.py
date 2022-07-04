from fastapi import APIRouter, HTTPException, status, Header, Response
from typing import Optional

from models.playlist import PlaylistModel, CreatePlaylistRequest, UpdatePlaylistRequest, AddSongsPlaylistRequest
from models.song import SongModel
import service.playlist
import service.artist
from utils.utils import log_request_body, validate_song, verify_api_key, check_valid_playlist_id, get_user_subscription
from exceptions.playlist_exceptions import PlaylistNotOwnedByUser


playlist_routes = APIRouter()


def _verify_ownership(playlist_id, user_id):
    if not service.playlist.is_owner(playlist_id, user_id):
        raise PlaylistNotOwnedByUser(playlist_id, user_id)


@playlist_routes.get("/playlists", response_model=list[PlaylistModel], tags=["Playlists"], status_code=status.HTTP_200_OK)
async def get_playlists(response: Response,
                        q: Optional[str] = None,
                        x_user_id: Optional[str] = Header(None),
                        x_api_key: Optional[str] = Header(None),
                        authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    return service.playlist.find(q)


@playlist_routes.get("/playlists/{playlist_id}", response_model=PlaylistModel, tags=["Playlists"], status_code=status.HTTP_200_OK)
async def get_playlist(response: Response,
                       playlist_id: str,
                       x_user_id: Optional[str] = Header(None),
                       x_api_key: Optional[str] = Header(None),
                       authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    check_valid_playlist_id(playlist_id)
    playlist = service.playlist.get(playlist_id)
    if playlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist {playlist_id} not found")

    return playlist


@playlist_routes.get("/playlists/{playlist_id}/songs", response_model=list[SongModel], tags=["Playlists"], status_code=status.HTTP_200_OK)
async def get_playlist_songs(response: Response,
                             playlist_id: str,
                             x_user_id: Optional[str] = Header(None),
                             x_api_key: Optional[str] = Header(None),
                             authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    check_valid_playlist_id(playlist_id)
    playlist_songs = service.playlist.get_songs(playlist_id, get_user_subscription(x_user_id))
    if playlist_songs is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist {playlist_id} not found")

    for song in playlist_songs:
        song['artists'] = [service.artist.get_name(artist_id) for artist_id in song['artists']]

    return playlist_songs


@playlist_routes.post("/playlists", response_model=PlaylistModel, tags=["Playlists"], status_code=status.HTTP_201_CREATED)
async def create_playlist(response: Response,
                          playlist: CreatePlaylistRequest,
                          x_request_id: Optional[str] = Header(None),
                          x_user_id: Optional[str] = Header(None),
                          x_api_key: Optional[str] = Header(None),
                          authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    for song in playlist.songs:
        validate_song(song)
    log_request_body(x_request_id, playlist)
    return service.playlist.create(playlist, x_user_id)


@playlist_routes.post("/playlists/{playlist_id}", response_model=PlaylistModel, tags=["Playlists"])
async def add_songs(response: Response,
                    playlist_id: str,
                    songs: AddSongsPlaylistRequest,
                    x_request_id: Optional[str] = Header(None),
                    x_user_id: Optional[str] = Header(None),
                    x_api_key: Optional[str] = Header(None),
                    authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    check_valid_playlist_id(playlist_id)
    _verify_ownership(playlist_id, x_user_id)
    for song in songs.songs:
        validate_song(song)
    log_request_body(x_request_id, songs)

    updated_playlist = service.playlist.add_songs(playlist_id, songs.songs)
    if not updated_playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist {playlist_id} not found")

    return updated_playlist


@playlist_routes.delete("/playlists/{playlist_id}/delete/{song_id}", response_model=PlaylistModel, tags=["Playlists"])
async def delete_song(response: Response,
                      playlist_id: str,
                      song_id: str,
                      x_request_id: Optional[str] = Header(None),
                      x_user_id: Optional[str] = Header(None),
                      x_api_key: Optional[str] = Header(None),
                      authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    check_valid_playlist_id(playlist_id)
    _verify_ownership(playlist_id, x_user_id)
    log_request_body(x_request_id, song_id)

    updated_playlist = service.playlist.delete_song(playlist_id, song_id)
    if not updated_playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist {playlist_id} not found")

    return updated_playlist


@playlist_routes.put("/playlists/{playlist_id}", response_model=PlaylistModel, tags=["Playlists"])
async def update_playlist(response: Response,
                          playlist_id: str,
                          playlist: UpdatePlaylistRequest,
                          x_request_id: Optional[str] = Header(None),
                          x_user_id: Optional[str] = Header(None),
                          x_api_key: Optional[str] = Header(None),
                          authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
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
async def delete_playlist(response: Response,
                          playlist_id: str,
                          x_user_id: Optional[str] = Header(None),
                          x_api_key: Optional[str] = Header(None),
                          authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    check_valid_playlist_id(playlist_id)
    r = service.playlist.delete(playlist_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist {playlist_id} not found")
