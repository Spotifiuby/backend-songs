from typing import Optional
from pydantic import BaseModel
import datetime


class AlbumModel(BaseModel):
    id: str
    name: str
    artists: list[str]
    songs: list[str]
    year: int
    date_created: datetime.datetime


class CreateAlbumRequest(BaseModel):
    name: str
    artists: list[str]
    songs: list[str]
    year: int


class UpdateAlbumRequest(BaseModel):
    name: Optional[str]
    artists: Optional[list]
    songs: Optional[list[str]]
    year: Optional[int]

