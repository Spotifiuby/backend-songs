from typing import Optional, Union
from pydantic import BaseModel
import datetime


class ArtistModel(BaseModel):
    id: str
    name: str
    user_id: str
    date_created: datetime.datetime


class CreateArtistRequest(BaseModel):
    name: str


class UpdateArtistRequest(BaseModel):
    name: Optional[str]
