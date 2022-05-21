from fastapi import APIRouter, HTTPException, status, Header, Depends

from models.album import AlbumModel, CreateAlbumRequest, UpdateAlbumRequest
import service.album
from typing import Optional
from utils.utils import log_request_body, validate_song, check_valid_album_id, verify_token

album_routes = APIRouter()


@album_routes.get("/albums", response_model=list[AlbumModel], tags=["Albums"], status_code=status.HTTP_200_OK)
async def get_albums(q: Optional[str] = None,
                     x_user_id: Optional[str] = Header(None),
                     x_api_key: Optional[str] = Header(None),
                     authorization: Optional[str] = Header(None)):
    verify_token(x_api_key)
    return service.album.find(q)


@album_routes.get("/albums/{album_id}", response_model=AlbumModel, tags=["Albums"], status_code=status.HTTP_200_OK)
async def get_album(album_id: str = Depends(check_valid_album_id),
                    x_user_id: Optional[str] = Header(None),
                    x_api_key: Optional[str] = Header(None),
                    authorization: Optional[str] = Header(None)):
    verify_token(x_api_key)
    album = service.album.get(album_id)
    if album is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Album {album_id} not found")

    return album


@album_routes.post("/albums", response_model=AlbumModel, tags=["Albums"], status_code=status.HTTP_201_CREATED)
async def create_album(album: CreateAlbumRequest, x_request_id: Optional[str] = Header(None),
                       x_user_id: Optional[str] = Header(None),
                       x_api_key: Optional[str] = Header(None),
                       authorization: Optional[str] = Header(None)):
    verify_token(x_api_key)
    for song in album.songs:
        validate_song(song)
    log_request_body(x_request_id, album)

    return service.album.create(album)


@album_routes.put("/albums/{album_id}/songs", response_model=AlbumModel, tags=["Albums"])
async def add_song(album_id: str = Depends(check_valid_album_id), song_id: str = Depends(validate_song),
                   x_request_id: Optional[str] = Header(None),
                   x_user_id: Optional[str] = Header(None),
                   x_api_key: Optional[str] = Header(None),
                   authorization: Optional[str] = Header(None)):
    verify_token(x_api_key)
    log_request_body(x_request_id, {"song": song_id})

    updated_album = service.album.add_song(album_id, song_id)
    if not updated_album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Album {album_id} not found")

    return updated_album


@album_routes.put("/albums/{album_id}/artists", response_model=AlbumModel, tags=["Albums"])
async def add_artist(album_id: str, artist: str,
                     x_request_id: Optional[str] = Header(None),
                     x_user_id: Optional[str] = Header(None),
                     x_api_key: Optional[str] = Header(None),
                     authorization: Optional[str] = Header(None)):
    verify_token(x_api_key)
    check_valid_album_id(album_id)
    log_request_body(x_request_id, {"artist": artist})

    updated_album = service.album.add_artist(album_id, artist)
    if not updated_album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Album {album_id} not found")

    return updated_album


@album_routes.put("/albums/{album_id}", response_model=AlbumModel, tags=["Albums"])
async def update_album(album_id: str, album: UpdateAlbumRequest,
                       x_request_id: Optional[str] = Header(None),
                       x_user_id: Optional[str] = Header(None),
                       x_api_key: Optional[str] = Header(None),
                       authorization: Optional[str] = Header(None)):
    verify_token(x_api_key)
    check_valid_album_id(album_id)
    if album.songs:
        for song in album.songs:
            validate_song(song)
    log_request_body(x_request_id, album)

    updated_album = service.album.update(album_id, album)
    if not updated_album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Album {album_id} not found")

    return updated_album


@album_routes.delete("/albums/{album_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Albums"])
async def delete_album(album_id: str = Depends(check_valid_album_id),
                       x_user_id: Optional[str] = Header(None),
                       x_api_key: Optional[str] = Header(None),
                       authorization: Optional[str] = Header(None)):
    verify_token(x_api_key)
    r = service.album.delete(album_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Album {album_id} not found")
