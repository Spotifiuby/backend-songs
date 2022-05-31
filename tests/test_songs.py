import pytest
from bson import ObjectId
import datetime
from fastapi.testclient import TestClient

from main import app
from config.db import conn
from tests.test_artists import TEST_ARTIST

TEST_SONG = {
    "_id": ObjectId("625c9dcd232be00e5f827f6a"),
    "status": "active",
    "name": "test",
    "artists": [
        TEST_ARTIST["_id"]
    ],
    "genre": "rock",
    "date_created": datetime.datetime.today(),
    "date_uploaded": None
}

client = TestClient(app)


@pytest.fixture()
def mongo_test_empty():
    conn.songs.delete_many({})
    conn.artists.delete_many({})


@pytest.fixture()
def mongo_test(mongo_test_empty):
    conn.songs.insert_one(TEST_SONG)
    conn.artists.insert_one(TEST_ARTIST)


@pytest.fixture()
def mongo_test_artist(mongo_test_empty):
    conn.artists.insert_one(TEST_ARTIST)


def test_get_all_songs_empty(mongo_test_empty):
    response = client.get("/songs")
    assert response.status_code == 200
    assert response.json() == []


def test_create_song(mongo_test):
    test_song = {"name": "test", "artists": [], "genre": "rock"}
    response = client.post("/songs", json=test_song, headers={'x-user-id': TEST_ARTIST['user_id']})
    assert response.status_code == 201
    assert len(response.json()) > 0
    response.json()["name"] = test_song["name"]
    response.json()["artists"] = test_song["artists"]
    response.json()["genre"] = test_song["genre"]


def test_get_all_songs(mongo_test_artist):
    test_song = {"name": "test", "artists": [str(TEST_ARTIST['_id'])], "genre": "rock"}
    for i in range(10):
        client.post("/songs", json=test_song, headers={'x-user-id': TEST_ARTIST['user_id']})
    response = client.get("/songs")
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_find_song(mongo_test_artist):
    test_song1 = {"name": "Across the universe", "artists": [], "genre": "rock"}
    test_song2 = {"name": "On the run", "artists": [], "genre": "rock"}
    response = client.post("/songs", json=test_song1, headers={'x-user-id': TEST_ARTIST['user_id']})
    assert response.status_code == 201
    response = client.post("/songs", json=test_song2, headers={'x-user-id': TEST_ARTIST['user_id']})
    assert response.status_code == 201
    response1 = client.get("/songs", params="q=the")
    assert len(response1.json()) == 2
    response2 = client.get("/songs", params="q=univ")
    assert len(response2.json()) == 1
    response2 = client.get("/songs", params="q=run")
    assert len(response2.json()) == 1
    response2 = client.get("/songs", params="q=other")
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
    expected_response['artists'] = [TEST_ARTIST['name']]
    del expected_response["_id"]
    del expected_response["date_created"]
    assert json_response == expected_response


def test_update_song(mongo_test):
    updated_song = {"name": "updated_name"}
    response = client.put("/songs/{}".format(str(TEST_SONG["_id"])), json=updated_song,
                          headers={'x-user-id': TEST_ARTIST['user_id']})
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()["name"] == updated_song["name"]
    assert response.json()["artists"] == [str(TEST_ARTIST['_id'])]


def test_update_song_not_found_fails(mongo_test_empty):
    updated_song = {"name": "updated_name", "artists": ["updated_artist"]}
    response = client.put("/songs/{}".format(str(TEST_SONG["_id"])), json=updated_song,
                          headers={'x-user-id': TEST_ARTIST['user_id']})
    assert response.status_code == 404


def test_delete_song(mongo_test):
    response = client.delete("/songs/{}".format(TEST_SONG["_id"]),
                             headers={'x-user-id': TEST_ARTIST['user_id']})
    assert response.status_code == 204
    response_get = client.get("/songs/{}".format(TEST_SONG["_id"]),
                              headers={'x-user-id': TEST_ARTIST['user_id']})
    assert response_get.status_code == 404


def test_delete_song_not_found_fails(mongo_test_empty):
    response = client.delete("/songs/{}".format(TEST_SONG["_id"]),
                             headers={'x-user-id': TEST_ARTIST['user_id']})
    assert response.status_code == 404


def test_get_invalid_id_fails(mongo_test):
    response_get = client.get("/songs/{}".format("123"))
    assert response_get.status_code == 400
