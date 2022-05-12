from fastapi import APIRouter, HTTPException, status, Header
from models.album import AlbumModel, CreateAlbumRequest, UpdateAlbumRequest
import service.album
from bson import ObjectId
from typing import Optional
from utils.utils import log_request_body, get_song_and_validate

album_routes = APIRouter()


@album_routes.get("/albums", response_model=list[AlbumModel], tags=["Albums"], status_code=status.HTTP_200_OK)
async def get_albums(q: Optional[str] = None):
    return service.album.find(q)


@album_routes.get("/albums/{album_id}", response_model=AlbumModel, tags=["Albums"], status_code=status.HTTP_200_OK)
async def get_album(album_id: str):
    _check_valid_album_id(album_id)
    album = service.album.get(album_id)
    if album is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Album {album_id} not found")

    return album


@album_routes.post("/albums", response_model=AlbumModel, tags=["Albums"], status_code=status.HTTP_201_CREATED)
async def create_album(album: CreateAlbumRequest, x_request_id: Optional[str] = Header(None)):
    for song in album.songs:
        get_song_and_validate(song)
    log_request_body(x_request_id, album)

    return service.album.create(album)


@album_routes.put("/albums/{album_id}/songs", response_model=AlbumModel, tags=["Albums"])
async def add_song(album_id: str, song: str, x_request_id: Optional[str] = Header(None)):
    _check_valid_album_id(album_id)
    get_song_and_validate(song)
    log_request_body(x_request_id, {"song": song})

    updated_album = service.album.add_song(album_id, song)
    if not updated_album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Album {album_id} not found")

    return updated_album


@album_routes.put("/albums/{album_id}/artists", response_model=AlbumModel, tags=["Albums"])
async def add_artist(album_id: str, artist: str, x_request_id: Optional[str] = Header(None)):
    _check_valid_album_id(album_id)
    log_request_body(x_request_id, {"artist": artist})

    updated_album = service.album.add_artist(album_id, artist)
    if not updated_album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Album {album_id} not found")

    return updated_album


@album_routes.put("/albums/{album_id}", response_model=AlbumModel, tags=["Albums"])
async def update_album(album_id: str, album: UpdateAlbumRequest, x_request_id: Optional[str] = Header(None)):
    _check_valid_album_id(album_id)
    if album.songs:
        for song in album.songs:
            get_song_and_validate(song)
    log_request_body(x_request_id, album)

    updated_album = service.album.update(album_id, album)
    if not updated_album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Album {album_id} not found")

    return updated_album


@album_routes.delete("/albums/{album_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Albums"])
async def delete_album(album_id: str):
    _check_valid_album_id(album_id)
    r = service.album.delete(album_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Album {album_id} not found")


def _check_valid_album_id(album_id):
    if not ObjectId.is_valid(album_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Album ID '{album_id}' is not valid")
