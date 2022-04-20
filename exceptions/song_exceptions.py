from fastapi import HTTPException, status


class SongNotFound(HTTPException):
    def __init__(self, song_id: str):
        super().__init__(status.HTTP_404_NOT_FOUND, f"Song not found {song_id}", None)


class SongNotAvailable(HTTPException):
    def __init__(self, song_id: str):
        super().__init__(status.HTTP_400_BAD_REQUEST, f"Song not available {song_id}", None)
