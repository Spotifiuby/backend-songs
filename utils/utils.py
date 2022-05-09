import asyncio
import logging

from bson import ObjectId
from fastapi import HTTPException
from starlette import status

import service.song
from exceptions.song_exceptions import SongNotFound, SongNotAvailable
from models.song import SongModel

logger = logging.getLogger('main-logger')


def log_request_body(request_id, body):
    asyncio.ensure_future(_log_request_body(request_id, body))


async def _log_request_body(request_id, body):
    logger.info(f"Request: {request_id} - Body: {body}")


def get_song_and_validate(song_id: str):
    check_valid_song_id(song_id)
    song = service.song.get(song_id)
    if not song:
        raise SongNotFound(song_id)
    if not _check_active_song(song):
        raise SongNotAvailable(song_id)


def check_valid_song_id(song_id):
    if not ObjectId.is_valid(song_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Song ID '{song_id}' is not valid")


def _check_active_song(song: dict):
    return SongModel.is_active(song)
