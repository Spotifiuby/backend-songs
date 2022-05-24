from fastapi import HTTPException, status


class ArtistNotFound(HTTPException):
    def __init__(self, artist_id: str):
        super().__init__(status.HTTP_404_NOT_FOUND, f"Artist not found {artist_id}", None)


class ArtistNotFoundForUser(HTTPException):
    def __init__(self, user_id: str):
        super().__init__(status.HTTP_404_NOT_FOUND, f"Artist not found for user {user_id}", None)
