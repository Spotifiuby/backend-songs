import asyncio
import logging

from bson import ObjectId
from fastapi import HTTPException, Depends
from starlette import status
import os

import service.song
from exceptions.song_exceptions import SongNotFound, SongNotAvailable
from models.song import SongModel

logger = logging.getLogger('main-logger')


def verify_token(token):
    if os.getenv("CURRENT_ENVIRONMENT") == "production" and token != os.getenv('GATEWAY_API_KEY'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Access token not valid")


def log_request_body(request_id, body):
    asyncio.ensure_future(_log_request_body(request_id, body))


async def _log_request_body(request_id, body):
    logger.info(f"Request: {request_id} - Body: {body}")


def check_valid_song_id(song_id):
    if not ObjectId.is_valid(song_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Song ID '{song_id}' is not valid")
    return song_id


def check_valid_artist_id(artist_id):
    if not ObjectId.is_valid(artist_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Artist ID '{artist_id}' is not valid")
    return artist_id


def check_valid_playlist_id(playlist_id):
    if not ObjectId.is_valid(playlist_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Artist ID '{playlist_id}' is not valid")
    return playlist_id


def check_valid_album_id(album_id):
    if not ObjectId.is_valid(album_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Artist ID '{album_id}' is not valid")
    return album_id


def _check_active_song(song: dict):
    return SongModel.is_active(song)


def validate_song(song_id: str = Depends(check_valid_song_id)):
    song = service.song.get(song_id)
    if not song:
        raise SongNotFound(song_id)
    if not _check_active_song(song):
        raise SongNotAvailable(song_id)
    return song_id
