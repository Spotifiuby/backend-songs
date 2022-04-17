from fastapi import APIRouter, Response
from service.content import get_song_content

content_routes = APIRouter()


@content_routes.get("/songs/{song_id}/content", response_class=Response, tags=["Content"])
async def get_content(song_id: str):
    contents = get_song_content(song_id)
    if contents:
        return Response(media_type="audio/mpeg3", content=contents)
    else:
        Response(status_code=404)
