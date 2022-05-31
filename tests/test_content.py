from fastapi.testclient import TestClient
from bson import ObjectId
import io
import pytest

from main import app
from models.song import StatusEnum
from config.db import conn
from config.db import bucket
from tests.test_artists import TEST_ARTIST

client = TestClient(app)

SONG_NOT_FOUND_ID = "625c9dcd232be00e5f827f7d"
SONG_NOT_AVAILABLE_ID = "625c9dcd232be00e5f827f7a"
CONTENT_NOT_FOUND_ID = "625c9dcd232be00e5f827f7b"
SONG_AND_CONTENT_OK = "625c9dcd232be00e5f827f7c"


@pytest.fixture()
def mongo_test_empty():
    conn.songs.delete_many({})
    conn.artists.delete_many({})


@pytest.fixture()
def mongo_test(mongo_test_empty):
    conn.songs.insert_one({"_id": ObjectId(SONG_NOT_AVAILABLE_ID), "status": StatusEnum.inactive, "artists": []})
    conn.songs.insert_one({"_id": ObjectId(CONTENT_NOT_FOUND_ID), "status": StatusEnum.not_uploaded, "artists": []})
    conn.songs.insert_one({"_id": ObjectId(f"{SONG_AND_CONTENT_OK}"), "status": StatusEnum.active, "artists": []})
    conn.artists.insert_one(TEST_ARTIST)
    bucket.blob(f"{SONG_AND_CONTENT_OK}/{SONG_AND_CONTENT_OK}.mp3").upload_from_string("content")


def test_get_content_not_found(mongo_test):
    response = client.get(f"/songs/{CONTENT_NOT_FOUND_ID}/content")
    assert response.status_code == 404
    assert response.json() == {'detail': f'Content not found for Song {CONTENT_NOT_FOUND_ID}'}


def test_get_content_song_not_found(mongo_test_empty):
    response = client.get(f"/songs/{SONG_NOT_FOUND_ID}/content")
    assert response.status_code == 404
    assert response.json() == {'detail': f'Song {SONG_NOT_FOUND_ID} not found'}


def test_get_content_song_not_available(mongo_test):
    response = client.get(f"/songs/{SONG_NOT_AVAILABLE_ID}/content")
    assert response.status_code == 400
    assert response.json() == {'detail': f'Song {SONG_NOT_AVAILABLE_ID} not available'}


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
    test_song = {"name": "test", "artists": [str(TEST_ARTIST['_id'])], "genre": "rock"}
    response = client.post("/songs", json=test_song, headers={'x-user-id': TEST_ARTIST['user_id']})
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
    test_song['id'] = song_id
    test_song['status'] = 'active'
    test_song['artists'] = [str(TEST_ARTIST['name'])]
    assert json_response == test_song
