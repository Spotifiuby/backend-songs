from fastapi import HTTPException, status


class ContentNotFound(HTTPException):
    def __init__(self, song_id: str):
        super().__init__(status.HTTP_404_NOT_FOUND, f"Content not found for Song {song_id}", None)


class ContentForbidden(HTTPException):
    def __init__(self, song_id: str, user_id: str):
        super().__init__(status.HTTP_403_FORBIDDEN, f"Cannot download content for Song:{song_id} for User:{user_id}.")
