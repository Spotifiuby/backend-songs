from fastapi import APIRouter, HTTPException, status, Header, Depends, Response
from typing import Optional

from models.album import AlbumModel, CreateAlbumRequest, UpdateAlbumRequest
from models.song import SongModel
import service.album
import service.artist
from utils.utils import log_request_body, validate_song, check_valid_album_id, check_valid_artist_id, verify_api_key, get_user_subscription

album_routes = APIRouter()


@album_routes.get("/albums", response_model=list[AlbumModel], tags=["Albums"], status_code=status.HTTP_200_OK)
async def get_albums(response: Response,
                     q: Optional[str] = None,
                     artist_id: Optional[str] = None,
                     x_user_id: Optional[str] = Header(None),
                     x_api_key: Optional[str] = Header(None),
                     authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    albums = service.album.find(q, artist_id, subscription_level=get_user_subscription(x_user_id))
    for album in albums:
        album['artists'] = [service.artist.get_name(artist_id) for artist_id in album['artists']]
    return albums


@album_routes.get("/albums/{album_id}", response_model=AlbumModel, tags=["Albums"], status_code=status.HTTP_200_OK)
async def get_album(response: Response,
                    album_id: str = Depends(check_valid_album_id),
                    x_user_id: Optional[str] = Header(None),
                    x_api_key: Optional[str] = Header(None),
                    authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    album = service.album.get(album_id)
    if album is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Album {album_id} not found")
    album['artists'] = [service.artist.get_name(artist_id) for artist_id in album['artists']]
    return album


@album_routes.get("/albums/{album_id}/songs", response_model=list[SongModel], tags=["Albums"], status_code=status.HTTP_200_OK)
async def get_album_songs(response: Response,
                          album_id: str,
                          x_user_id: Optional[str] = Header(None),
                          x_api_key: Optional[str] = Header(None),
                          authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    check_valid_album_id(album_id)
    album_songs = service.album.get_songs(album_id, get_user_subscription(x_user_id))
    if album_songs is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Album {album_id} not found")

    for song in album_songs:
        song['artists'] = [service.artist.get_name(artist_id) for artist_id in song['artists']]

    return album_songs


@album_routes.post("/albums", response_model=AlbumModel, tags=["Albums"], status_code=status.HTTP_201_CREATED)
async def create_album(response: Response,
                       album: CreateAlbumRequest,
                       x_request_id: Optional[str] = Header(None),
                       x_user_id: Optional[str] = Header(None),
                       x_api_key: Optional[str] = Header(None),
                       authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    for song in album.songs:
        validate_song(song)
    log_request_body(x_request_id, album)

    return service.album.create(album)


@album_routes.put("/albums/{album_id}/songs", response_model=AlbumModel, tags=["Albums"])
async def add_song(response:  Response,
                   album_id: str = Depends(check_valid_album_id), song_id: str = Depends(validate_song),
                   x_request_id: Optional[str] = Header(None),
                   x_user_id: Optional[str] = Header(None),
                   x_api_key: Optional[str] = Header(None),
                   authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    log_request_body(x_request_id, {"song": song_id})

    updated_album = service.album.add_song(album_id, song_id)
    if not updated_album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Album {album_id} not found")

    return updated_album


@album_routes.put("/albums/{album_id}/artists", response_model=AlbumModel, tags=["Albums"])
async def add_artist(response: Response,
                     album_id: str,
                     artist_id: str,
                     x_request_id: Optional[str] = Header(None),
                     x_user_id: Optional[str] = Header(None),
                     x_api_key: Optional[str] = Header(None),
                     authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    check_valid_album_id(album_id)
    check_valid_artist_id(artist_id)
    log_request_body(x_request_id, {"artist_id": artist_id})

    updated_album = service.album.add_artist(album_id, artist_id)
    if not updated_album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Album {album_id} not found")

    return updated_album


@album_routes.put("/albums/{album_id}", response_model=AlbumModel, tags=["Albums"])
async def update_album(response: Response,
                       album_id: str, album: UpdateAlbumRequest,
                       x_request_id: Optional[str] = Header(None),
                       x_user_id: Optional[str] = Header(None),
                       x_api_key: Optional[str] = Header(None),
                       authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
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
async def delete_album(response: Response,
                       album_id: str = Depends(check_valid_album_id),
                       x_user_id: Optional[str] = Header(None),
                       x_api_key: Optional[str] = Header(None),
                       authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    r = service.album.delete(album_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Album {album_id} not found")
