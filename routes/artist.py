from fastapi import APIRouter, HTTPException, status, Header, Depends, Response
from typing import Optional

from utils.utils import log_request_body, check_valid_artist_id, verify_api_key
from models.artist import ArtistModel, CreateArtistRequest, UpdateArtistRequest
import service.artist

artist_routes = APIRouter()


@artist_routes.get("/artists", response_model=list[ArtistModel], tags=["Artists"], status_code=status.HTTP_200_OK)
async def get_artists(response: Response,
                      q: Optional[str] = None,
                      x_user_id: Optional[str] = Header(None),
                      x_api_key: Optional[str] = Header(None),
                      authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    return service.artist.find(q)


@artist_routes.get("/artists/{artist_id}", response_model=ArtistModel, tags=["Artists"], status_code=status.HTTP_200_OK)
async def get_artist(response: Response,
                     artist_id: str = Depends(check_valid_artist_id),
                     x_user_id: Optional[str] = Header(None),
                     x_api_key: Optional[str] = Header(None),
                     authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    artist = service.artist.get(artist_id)
    if artist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Artist {artist_id} not found")

    return artist


@artist_routes.post("/artists", response_model=ArtistModel, tags=["Artists"], status_code=status.HTTP_201_CREATED)
async def create_artist(response: Response,
                        artist: CreateArtistRequest,
                        x_user_id: Optional[str] = Header(None),
                        x_api_key: Optional[str] = Header(None),
                        authorization: Optional[str] = Header(None),
                        x_request_id: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    log_request_body(x_request_id, artist)
    verify_api_key(x_api_key)
    if not x_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="x_user_id is missing")
    return service.artist.create(artist.name, artist.subscription_level, x_user_id)


@artist_routes.put("/artists/{artist_id}", response_model=ArtistModel, tags=["Artists"])
async def update_artist(response: Response,
                        artist_id: str = Depends(check_valid_artist_id),
                        artist: UpdateArtistRequest = None,
                        x_user_id: Optional[str] = Header(None),
                        x_api_key: Optional[str] = Header(None),
                        authorization: Optional[str] = Header(None),
                        x_request_id: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    log_request_body(x_request_id, artist)
    verify_api_key(x_api_key)
    updated_artist = service.artist.update(artist_id,
                                           name=artist.name,
                                           subscription_level=artist.subscription_level)
    if not updated_artist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Artist {artist_id} not found")
    return updated_artist


@artist_routes.delete("/artists/{artist_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Artists"])
async def delete_artist(response: Response,
                        artist_id: str = Depends(check_valid_artist_id),
                        x_user_id: Optional[str] = Header(None),
                        x_api_key: Optional[str] = Header(None),
                        authorization: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    verify_api_key(x_api_key)
    r = service.artist.delete(artist_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Artist {artist_id} not found")


