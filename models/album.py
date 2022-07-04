from typing import Optional, Union
from pydantic import BaseModel
import datetime


class AlbumModel(BaseModel):
    id: str
    name: str
    artists: list[str]
    songs: list[str]
    year: int
    cover: Union[str, None]
    date_created: datetime.datetime


class CreateAlbumRequest(BaseModel):
    name: str
    artists: list[str]
    songs: list[str]
    year: int
    cover: Optional[str]


class UpdateAlbumRequest(BaseModel):
    name: Optional[str]
    artists: Optional[list]
    songs: Optional[list[str]]
    year: Optional[int]
    cover: Optional[str]
