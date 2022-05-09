from fastapi import APIRouter, HTTPException, status
from models.playlist import PlaylistModel, CreatePlaylistRequest, UpdatePlaylistRequest
import service.playlist
from bson import ObjectId

playlist_routes = APIRouter()


@playlist_routes.get("/playlists", response_model=list[PlaylistModel], tags=["Playlists"], status_code=status.HTTP_200_OK)
async def get_playlists():
    return service.playlist.get_all()


@playlist_routes.get("/playlists/{playlist_id}", response_model=PlaylistModel, tags=["Playlists"], status_code=status.HTTP_200_OK)
async def get_playlist(playlist_id: str):
    _check_valid_playlist_id(playlist_id)
    playlist = service.playlist.get(playlist_id)
    if playlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist {playlist_id} not found")

    return playlist


@playlist_routes.post("/playlists", response_model=PlaylistModel, tags=["Playlists"], status_code=status.HTTP_201_CREATED)
async def create_playlist(playlist: CreatePlaylistRequest):
    return service.playlist.create(playlist)


@playlist_routes.put("/playlists/{playlist_id}/songs", response_model=PlaylistModel, tags=["Playlists"])
async def add_song(playlist_id: str, song: str):
    _check_valid_playlist_id(playlist_id)
    updated_playlist = service.playlist.add_song(playlist_id, song)
    if not updated_playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist {playlist_id} not found")

    return updated_playlist


@playlist_routes.put("/playlists/{playlist_id}", response_model=PlaylistModel, tags=["Playlists"])
async def update_playlist(playlist_id: str, playlist: UpdatePlaylistRequest):
    _check_valid_playlist_id(playlist_id)
    updated_playlist = service.playlist.update(playlist_id, playlist)
    if not updated_playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist {playlist_id} not found")

    return updated_playlist


@playlist_routes.delete("/playlists/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Playlists"])
async def delete_playlist(playlist_id: str):
    _check_valid_playlist_id(playlist_id)
    r = service.playlist.delete(playlist_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Playlist {playlist_id} not found")


def _check_valid_playlist_id(playlist_id):
    if not ObjectId.is_valid(playlist_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Playlist ID '{playlist_id}' is not valid")
