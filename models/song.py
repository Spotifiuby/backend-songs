from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel
import datetime


class StatusEnum(str, Enum):
    not_uploaded = "not_uploaded"
    active = "active"
    inactive = "inactive"


class SongModel(BaseModel):
    id: str
    name: str
    artists: list[str]
    genre: str
    status: StatusEnum
    date_created: datetime.datetime
    date_uploaded: Union[datetime.datetime, None]

    @staticmethod
    def is_active(song: dict):
        return "status" in song and song["status"] in ACTIVE_STATUSES


class CreateSongRequest(BaseModel):
    name: str
    artists: Optional[list[str]]
    genre: str


class UpdateSongRequest(BaseModel):
    name: Optional[str]
    artists: Optional[list]
    genre: Optional[str]
    status: Optional[StatusEnum]


# Definitions
ACTIVE_STATUSES = [StatusEnum.not_uploaded, StatusEnum.active]
