from typing import Optional
from pydantic import BaseModel
import datetime


class PlaylistModel(BaseModel):
    id: str
    name: str
    owner: str
    songs: list[str]
    date_created: datetime.datetime


class CreatePlaylistRequest(BaseModel):
    name: str
    owner: str
    songs: list[str]


class UpdatePlaylistRequest(BaseModel):
    name: Optional[str]
    owner: str
    songs: list[str]

