from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
import pymongo
from config.db import conn
from models.song import SongModel, UpdateSongRequest


def song_entity(song) -> dict:
    song["id"] = str(song.pop("_id"))
    return song


song_routes = APIRouter()


@song_routes.get("/songs", response_model=list[SongModel], tags=["songs"], status_code=status.HTTP_200_OK)
async def get_songs():
    songs = [song_entity(song) for song in conn.songs.find()]
    return songs


@song_routes.get("/songs/{song_id}", response_model=SongModel, tags=["songs"], status_code=status.HTTP_200_OK)
async def get_song(song_id: str):
    song = conn.songs.find_one({"_id": ObjectId(song_id)})
    if song is None:
        raise HTTPException(status_code=404, detail=f"Song {song_id} not found")

    return song_entity(song)


@song_routes.post("/songs", response_model=SongModel, tags=["songs"], status_code=status.HTTP_201_CREATED)
async def create_song(song: SongModel):
    r = conn.songs.insert_one(song.dict())
    mongo_song = conn.songs.find_one({"_id": r.inserted_id})

    return song_entity(mongo_song)


@song_routes.put("/songs/{id}", response_model=SongModel, tags=["songs"])
async def update_song(song_id: str, song: UpdateSongRequest):
    updated_song = {k: v for k, v in song.dict().items() if v is not None}
    updated_song = conn.songs.find_one_and_update(
        {"_id": ObjectId(song_id)},
        {"$set": dict(updated_song)},
        return_document=pymongo.ReturnDocument.AFTER
    )
    if not updated_song:
        raise HTTPException(status_code=404, detail=f"Song {song_id} not found")

    return song_entity(updated_song)


@song_routes.delete("/songs/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["songs"])
async def delete_song(song_id: str):
    if not ObjectId.is_valid(song_id):
        raise HTTPException(status_code=404, detail=f"id {song_id} is not valid")
    r = conn.songs.delete_one({"_id": ObjectId(song_id)})
    if r.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Song {song_id} not found")
