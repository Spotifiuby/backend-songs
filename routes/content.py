from fastapi import APIRouter, Response, UploadFile, status, Depends, Header
from typing import Optional

from exceptions.content_exceptions import ContentNotFound
from service.content import get_song_content, upload_song_content, verify_download
import service.song
import service.artist
from utils.utils import validate_song, verify_api_key, log_request_body
import requests

content_routes = APIRouter()


@content_routes.get("/songs/{song_id}/content", response_class=Response, tags=["Content"])
async def get_content(response: Response,
                      song_id: str = Depends(validate_song),
                      authorization: Optional[str] = Header(None),
                      x_user_id: Optional[str] = Header(None),
                      x_api_key: Optional[str] = Header(None),
                      x_request_id: Optional[str] = Header(None)):

    contents = get_song_content(song_id)
    if contents:

        song = service.song.get(song_id)
        if song:
            for artist_id in song['artists']:
                artist = service.artist.get(artist_id)
                user_id = artist['user_id']
                rBody = {
                    "amountInEthers": str(price),
                    "senderId": user_id,
                    }
                r = requests.post("https://spotifiuby-payment-service.herokuapp.com/deposit", json=rBody)
        # song = service.song.get(song_id)
        # if song is None:
        #     raise SongNotFound(song_id)
        # song['artists'] = [service.artist.get_name(artist_id) for artist_id in song['artists']]

        return Response(media_type="audio/mpeg", content=contents)
    else:
        raise ContentNotFound(song_id)


@content_routes.post("/songs/{song_id}/content", response_class=Response, tags=["Content"])
async def post_content(response: Response,
                       song_id: str = Depends(validate_song),
                       file: UploadFile = None,
                       x_user_id: Optional[str] = Header(None),
                       x_api_key: Optional[str] = Header(None),
                       authorization: Optional[str] = Header(None),
                       x_request_id: Optional[str] = Header(None)):
    if authorization:
        response.headers['authorization'] = authorization
    log_request_body(x_request_id, {'headers': {'authorization': authorization, 'x_api_key': x_api_key, 'x_user_id': x_user_id}})
    verify_api_key(x_api_key)
    upload_song_content(song_id, await file.read())
    service.song.activate_song(song_id)
    return Response(status_code=status.HTTP_201_CREATED)
