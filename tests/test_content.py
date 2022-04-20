from fastapi.testclient import TestClient
from bson import ObjectId
from main import app
from config.db import conn
from config.db import bucket
import io
import pytest

client = TestClient(app)


@pytest.fixture()
def mongo_test_empty():
    conn.songs.delete_many({})


@pytest.fixture()
def mongo_test(mongo_test_empty):
    conn.songs.insert_one({"_id": ObjectId("625c9dcd232be00e5f827f7b"), "status": "active"})
    conn.songs.insert_one({"_id": ObjectId("625c9dcd232be00e5f827f7c"), "status": "active"})
    bucket.blob("625c9dcd232be00e5f827f7c/625c9dcd232be00e5f827f7c.mp3").upload_from_string("content")


def test_get_content_not_found(mongo_test):
    response = client.get("/songs/625c9dcd232be00e5f827f7b/content")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Content not found for Song 625c9dcd232be00e5f827f7b'}


def test_get_content_song_not_found(mongo_test_empty):
    response = client.get("/songs/625c9dcd232be00e5f827f7b/content")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Song not found 625c9dcd232be00e5f827f7b'}


def test_create_content(mongo_test):
    f = io.StringIO("content")
    response = client.post("/songs/625c9dcd232be00e5f827f7b/content", files={"file": ("file.mp3", f)})
    assert response.status_code == 201


def test_get_content(mongo_test):
    response = client.get("/songs/625c9dcd232be00e5f827f7b/content")
    assert response.status_code == 200
    assert response.content == b"content"
    assert response.headers["content-type"] == "audio/mpeg"


def test_create_and_get_song_and_content(mongo_test):
    response = client.post("/songs", json={"name": "test", "artist": "test"})
    assert response.status_code == 201
    assert len(response.json()) > 0
    response.json()["name"] = "test"
    song_id = response.json()["id"]

    f = io.StringIO("test-content")
    response = client.post(f"/songs/{song_id}/content", files={"file": ("file.mp3", f)})
    assert response.status_code == 201

    response = client.get(f"/songs/{song_id}/content")
    assert response.status_code == 200
    assert response.content == b"test-content"
    assert response.headers["content-type"] == "audio/mpeg"

    response = client.get(f"/songs/{song_id}")
    assert response.status_code == 200
    assert response.json() == {'artist': 'test', 'id': f'{song_id}', 'name': 'test', 'status': 'active'}
