from fastapi.testclient import TestClient
from models.song import StatusEnum
from bson import ObjectId
from main import app
from config.db import conn
from config.db import bucket
import io
import pytest

client = TestClient(app)

SONG_NOT_FOUND_ID = "625c9dcd232be00e5f827f7d"
SONG_NOT_AVAILABLE_ID = "625c9dcd232be00e5f827f7a"
CONTENT_NOT_FOUND_ID = "625c9dcd232be00e5f827f7b"
SONG_AND_CONTENT_OK = "625c9dcd232be00e5f827f7c"


@pytest.fixture()
def mongo_test_empty():
    conn.songs.delete_many({})


@pytest.fixture()
def mongo_test(mongo_test_empty):
    conn.songs.insert_one({"_id": ObjectId(SONG_NOT_AVAILABLE_ID), "status": StatusEnum.inactive})
    conn.songs.insert_one({"_id": ObjectId(CONTENT_NOT_FOUND_ID), "status": StatusEnum.not_uploaded})
    conn.songs.insert_one({"_id": ObjectId(f"{SONG_AND_CONTENT_OK}"), "status": StatusEnum.active})
    bucket.blob(f"{SONG_AND_CONTENT_OK}/{SONG_AND_CONTENT_OK}.mp3").upload_from_string("content")


def test_get_content_not_found(mongo_test):
    response = client.get(f"/songs/{CONTENT_NOT_FOUND_ID}/content")
    assert response.status_code == 404
    assert response.json() == {'detail': f'Content not found for Song {CONTENT_NOT_FOUND_ID}'}


def test_get_content_song_not_found(mongo_test_empty):
    response = client.get(f"/songs/{SONG_NOT_FOUND_ID}/content")
    assert response.status_code == 404
    assert response.json() == {'detail': f'Song not found {SONG_NOT_FOUND_ID}'}


def test_get_content_song_not_available(mongo_test):
    response = client.get(f"/songs/{SONG_NOT_AVAILABLE_ID}/content")
    assert response.status_code == 400
    assert response.json() == {'detail': f'Song not available {SONG_NOT_AVAILABLE_ID}'}


def test_create_content(mongo_test):
    f = io.StringIO("content")
    response = client.post(f"/songs/{CONTENT_NOT_FOUND_ID}/content", files={"file": ("file.mp3", f)})
    assert response.status_code == 201
    assert conn.songs.find_one({"_id": ObjectId(CONTENT_NOT_FOUND_ID)})["status"] == "active"


def test_get_content(mongo_test):
    response = client.get(f"/songs/{SONG_AND_CONTENT_OK}/content")
    assert response.status_code == 200
    assert response.content == b"content"
    assert response.headers["content-type"] == "audio/mpeg"


def test_create_and_get_song_and_content(mongo_test):
    response = client.post("/songs", json={"name": "test", "artists": ["test"]})
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
    json_response = response.json()
    assert json_response["date_created"]
    assert json_response["date_uploaded"]
    del json_response["date_created"]
    del json_response["date_uploaded"]
    assert json_response == {'artists': ['test'], 'id': f'{song_id}', 'name': 'test', 'status': 'active'}
