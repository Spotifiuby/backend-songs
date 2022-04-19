import pytest
from main import app
from fastapi.testclient import TestClient
from config.db import conn
from config.db import bucket

client = TestClient(app)


@pytest.fixture()
def mongo_test():
    conn.songs.delete_many({})
    conn.songs.insert_one({"_id": "625c9dcd232be00e5f827f7b", "status": "active"})
    conn.songs.insert_one({"_id": "625c9dcd232be00e5f827f7c", "status": "active"})
    bucket.blob("625c9dcd232be00e5f827f7c/625c9dcd232be00e5f827f7c.mp3").upload_from_string("content")


def test_get_content_not_found(mongo_test):
    response = client.get("/songs/625c9dcd232be00e5f827f7b/content")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Content not found for song 625c9dcd232be00e5f827f7b'}


def test_create_content(mongo_test):
    with open("/Users/ndegiacomo/Downloads/file.mp3", "rb") as f:
        response = client.post("/songs/625c9dcd232be00e5f827f7b/content", files={"file": ("file.mp3", f)})
    assert response.status_code == 201


def test_get_content(mongo_test):
    response = client.get("/songs/625c9dcd232be00e5f827f7c/content")
    assert response.status_code == 200
    assert response.content == b"content"
    assert response.headers["content-type"] == "audio/mpeg3"
