import pytest
from bson import ObjectId
import datetime
from main import app
from fastapi.testclient import TestClient
from config.db import conn

TEST_SONG = {
    "_id": ObjectId("625c9dcd232be00e5f827f6a"),
    "status": "active",
    "name": "test",
    "artists": ["test"],
    "genre": "rock",
    "date_created": datetime.datetime.today(),
    "date_uploaded": None
}

client = TestClient(app)


@pytest.fixture()
def mongo_test_empty():
    conn.songs.delete_many({})


@pytest.fixture()
def mongo_test(mongo_test_empty):
    conn.songs.insert_one(TEST_SONG)


def test_get_all_songs_empty(mongo_test_empty):
    response = client.get("/songs")
    assert response.status_code == 200
    assert response.json() == []


def test_create_song(mongo_test):
    test_song = {"name": "test", "artists": ["test"], "genre": "rock"}
    response = client.post("/songs", json=test_song)
    assert response.status_code == 201
    assert len(response.json()) > 0
    response.json()["name"] = test_song["name"]
    response.json()["artists"] = test_song["artists"]
    response.json()["genre"] = test_song["genre"]


def test_get_all_songs(mongo_test_empty):
    test_song = {"name": "test", "artists": ["test"], "genre": "rock"}
    for i in range(10):
        client.post("/songs", json=test_song)
    response = client.get("/songs")
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_find_song(mongo_test_empty):
    test_song1 = {"name": "Let it be", "artists": ["The Beatles"], "genre": "rock"}
    test_song2 = {"name": "Time", "artists": ["Pink Floyd"], "genre": "rock"}
    client.post("/songs", json=test_song1)
    client.post("/songs", json=test_song2)
    response1 = client.get("/songs", params="q=rock")
    assert len(response1.json()) == 2
    response2 = client.get("/songs", params="q=beatles")
    assert len(response2.json()) == 1
    response2 = client.get("/songs", params="q=let")
    assert len(response2.json()) == 1
    response2 = client.get("/songs", params="q=rolling")
    assert len(response2.json()) == 0


def test_get_song_not_found(mongo_test):
    song_id = "625c9dcd232be00e5f827f7b"
    response = client.get("/songs/{}".format(song_id))
    assert response.status_code == 404
    assert response.json() == {"detail": "Song {} not found".format(song_id)}


def test_get_song(mongo_test):
    response = client.get("/songs/{}".format(str(TEST_SONG["_id"])))
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["date_created"]
    del json_response["date_created"]
    expected_response = TEST_SONG.copy()
    expected_response['id'] = str(expected_response['_id'])
    del expected_response["_id"]
    del expected_response["date_created"]
    assert json_response == expected_response


def test_update_song(mongo_test):
    updated_song = {"name": "updated_name", "artists": ["updated_artist"]}
    response = client.put("/songs/{}".format(str(TEST_SONG["_id"])), json=updated_song)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()["name"] == updated_song["name"]
    assert response.json()["artists"] == updated_song["artists"]


def test_update_song_not_found_fails(mongo_test_empty):
    updated_song = {"name": "updated_name", "artists": ["updated_artist"]}
    response = client.put("/songs/{}".format(str(TEST_SONG["_id"])), json=updated_song)
    assert response.status_code == 404


def test_delete_song(mongo_test):
    response = client.delete("/songs/{}".format(TEST_SONG["_id"]))
    assert response.status_code == 204
    response_get = client.get("/songs/{}".format(TEST_SONG["_id"]))
    assert response_get.status_code == 404


def test_delete_song_not_found_fails(mongo_test_empty):
    response = client.delete("/songs/{}".format(TEST_SONG["_id"]))
    assert response.status_code == 404


def test_get_invalid_id_fails(mongo_test):
    response_get = client.get("/songs/{}".format("123"))
    assert response_get.status_code == 400
