from fastapi import HTTPException, status


class ContentNotFound(HTTPException):
    def __init__(self, song_id: str):
        super().__init__(status.HTTP_404_NOT_FOUND, f"Content not found for Song {song_id}", None)

