from fastapi import HTTPException, status


class SongNotFound(HTTPException):
    def __init__(self, song_id: str):
        super().__init__(status.HTTP_404_NOT_FOUND, f"Song {song_id} not found", None)


class SongNotAvailable(HTTPException):
    def __init__(self, song_id: str):
        super().__init__(status.HTTP_400_BAD_REQUEST, f"Song {song_id} not available", None)


class SongNotOwnedByUser(HTTPException):
    def __init__(self, song_id: str, user_id: str):
        super().__init__(status.HTTP_400_BAD_REQUEST, f"The owner of song {song_id} is not {user_id}", None)
