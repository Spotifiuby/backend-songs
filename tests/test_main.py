from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_all_songs_empty():
    response = client.get("/songs")
    assert response.status_code == 200
    assert response.json() == []


def test_get_song_not_found():
    response = client.get("/songs/625c9dcd232be00e5f827f7b")
    assert response.status_code == 404
    assert response.json() == {"detail": "Song 625c9dcd232be00e5f827f7b not found"}


def test_get_content_not_found():
    response = client.get("/songs/625c9dcd232be00e5f827f7b/content")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Content not found for song 625c9dcd232be00e5f827f7b'}
