from fastapi import APIRouter, HTTPException, status
from models.song import SongModel, CreateSongRequest, UpdateSongRequest
import service.song
from bson import ObjectId

song_routes = APIRouter()


@song_routes.get("/songs", response_model=list[SongModel], tags=["Songs"], status_code=status.HTTP_200_OK)
async def get_songs():
    return service.song.get_all()


@song_routes.get("/songs/{song_id}", response_model=SongModel, tags=["Songs"], status_code=status.HTTP_200_OK)
async def get_song(song_id: str):
    _check_valid_song_id(song_id)
    song = service.song.get(song_id)
    if song is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Song {song_id} not found")

    return song


@song_routes.post("/songs", response_model=SongModel, tags=["Songs"], status_code=status.HTTP_201_CREATED)
async def create_song(song: CreateSongRequest):
    return service.song.create(song)


@song_routes.put("/songs/{id}", response_model=SongModel, tags=["Songs"])
async def update_song(song_id: str, song: UpdateSongRequest):
    _check_valid_song_id(song_id)
    updated_song = service.song.update(song_id, song)
    if not updated_song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Song {song_id} not found")

    return updated_song


@song_routes.delete("/songs/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Songs"])
async def delete_song(song_id: str):
    _check_valid_song_id(song_id)
    r = service.song.delete(song_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Song {song_id} not found")


def _check_valid_song_id(song_id):
    if not ObjectId.is_valid(song_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Song ID '{song_id}' is not valid")
