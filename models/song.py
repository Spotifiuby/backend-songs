from typing import Optional
from pydantic import BaseModel


class SongModel(BaseModel):
    id: str
    name: str
    artist: str


class UpdateSongRequest(BaseModel):
    name: Optional[str]
    artist: Optional[str]
