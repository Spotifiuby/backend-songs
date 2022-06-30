from typing import Optional, Union
from pydantic import BaseModel
import datetime


class ArtistModel(BaseModel):
    id: str
    name: str
    user_id: str
    subscription_level: int
    date_created: datetime.datetime


class CreateArtistRequest(BaseModel):
    name: str
    subscription_level: Optional[int]


class UpdateArtistRequest(BaseModel):
    name: Optional[str]
    subscription_level: Optional[int]
