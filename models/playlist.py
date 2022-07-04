from typing import Optional, Union
from pydantic import BaseModel
import datetime


class PlaylistModel(BaseModel):
    id: str
    name: str
    owner: str
    songs: list[str]
    cover: Union[str, None]
    date_created: datetime.datetime


class CreatePlaylistRequest(BaseModel):
    name: str
    songs: list[str]
    cover: Optional[str]


class UpdatePlaylistRequest(BaseModel):
    name: Optional[str]
    owner: Optional[str]
    songs: Optional[list[str]]
    cover: Optional[str]


class AddSongsPlaylistRequest(BaseModel):
    songs: list[str]
