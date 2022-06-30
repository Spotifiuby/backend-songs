from fastapi import HTTPException, status


class PlaylistNotFound(HTTPException):
    def __init__(self, playlist_id: str):
        super().__init__(status.HTTP_404_NOT_FOUND, f"Playlist {playlist_id} not found", None)


class PlaylistNotAvailable(HTTPException):
    def __init__(self, playlist_id: str):
        super().__init__(status.HTTP_400_BAD_REQUEST, f"Playlist {playlist_id} not available", None)


class PlaylistNotOwnedByUser(HTTPException):
    def __init__(self, playlist_id: str, user_id: str):
        super().__init__(status.HTTP_400_BAD_REQUEST, f"The owner of playlist {playlist_id} is not {user_id}", None)
