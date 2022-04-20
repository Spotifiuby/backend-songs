from enum import Enum
from typing import Optional
from pydantic import BaseModel


class StatusEnum(str, Enum):
    not_uploaded = "not_uploaded"
    active = "active"
    inactive = "inactive"


class SongModel(BaseModel):
    id: str
    name: str
    artist: str
    status: StatusEnum

    @staticmethod
    def is_active(song: dict):
        return "status" in song and song["status"] in ACTIVE_STATUSES


class CreateSongRequest(BaseModel):
    name: str
    artist: str


class UpdateSongRequest(BaseModel):
    name: Optional[str]
    artist: Optional[str]


# Definitions
ACTIVE_STATUSES = [StatusEnum.not_uploaded, StatusEnum.active]
