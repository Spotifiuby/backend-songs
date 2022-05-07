from typing import Optional
from pydantic import BaseModel
import datetime


class AlbumModel(BaseModel):
    id: str
    name: str
    artists: list[str]
    songs: list[str]
    date_created: datetime.datetime


class CreateAlbumRequest(BaseModel):
    name: str
    artists: list[str]
    songs: list[str]


class UpdateAlbumRequest(BaseModel):
    name: Optional[str]
    artists: Optional[list]
    songs: list[str]

