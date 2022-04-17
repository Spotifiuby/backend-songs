from fastapi import APIRouter, Response, HTTPException
from service.content import get_song_content

content_routes = APIRouter()


@content_routes.get("/songs/{song_id}/content", response_class=Response, tags=["Content"])
async def get_content(song_id: str):
    contents = get_song_content(song_id)
    if contents:
        return Response(media_type="audio/mpeg3", content=contents)
    else:
        raise HTTPException(status_code=404, detail=f"Content not found for song {song_id}")
