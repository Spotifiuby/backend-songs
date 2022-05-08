import pytest
from bson import ObjectId
import datetime
from main import app
from fastapi.testclient import TestClient
from config.db import conn

client = TestClient(app)

TEST_PLAYLIST = {
    "_id": ObjectId("625c9dcd232be00e5f827f6a"),
    "name": "test_name",
    "owner": "test_user",
    "songs": [
        "test_song_1",
        "test_song_2"
    ],
    "date_created": datetime.datetime.today(),
}


@pytest.fixture()
def mongo_test_empty():
    conn.playlists.delete_many({})


@pytest.fixture()
def mongo_test(mongo_test_empty):
    conn.playlists.insert_one(TEST_PLAYLIST)


def test_get_all_playlists_empty(mongo_test_empty):
    response = client.get("/playlists")
    assert response.status_code == 200
    assert response.json() == []


def test_create_playlist(mongo_test):
    test_playlist = {"name": "test", "owner": "test_owner", "songs": ["song_1", "song_2"]}
    response = client.post("/playlists", json=test_playlist)
    assert response.status_code == 201
    assert len(response.json()) > 0
    assert response.json()["name"] == test_playlist["name"]
    assert response.json()["owner"] == test_playlist["owner"]
    assert response.json()["songs"] == test_playlist["songs"]


def test_get_all_playlists(mongo_test_empty):
    test_playlist = {"name": "test", "owner": "test_owner", "songs": ["song_1", "song_2"]}
    for i in range(10):
        client.post("/playlists", json=test_playlist)
    response = client.get("/playlists")
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_get_playlist_not_found(mongo_test):
    _id = "625c9dcd232be00e5f827f7b"
    response = client.get("/playlists/{}".format(_id))
    assert response.status_code == 404
    assert response.json() == {"detail": "Playlist {} not found".format(_id)}


def test_get_playlist(mongo_test):
    response = client.get("/playlists/{}".format(str(TEST_PLAYLIST["_id"])))
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["date_created"]
    del json_response["date_created"]
    expected_response = TEST_PLAYLIST.copy()
    expected_response['id'] = str(expected_response['_id'])
    del expected_response["_id"]
    del expected_response["date_created"]
    assert json_response == expected_response


def test_add_song(mongo_test):
    new_song = "new_song"
    response = client.put("/playlists/{}/songs".format(str(TEST_PLAYLIST["_id"])), params={'song': new_song})
    assert response.status_code == 200
    json_response = response.json()
    expected_songs = TEST_PLAYLIST["songs"].copy()
    expected_songs.append(new_song)
    assert json_response["songs"] == expected_songs


def test_add_song_to_playlist_not_found_fails(mongo_test_empty):
    new_song = "new_song"
    response = client.put("/playlists/{}/songs".format(str(TEST_PLAYLIST["_id"])), params={'song': new_song})
    assert response.status_code == 404


def test_update_playlist(mongo_test):
    updated_playlist = {"name": "updated_name", "owner": "updated_owner", "songs": ["updated_song"]}
    response = client.put("/playlists/{}".format(str(TEST_PLAYLIST["_id"])), json=updated_playlist)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()["name"] == updated_playlist["name"]
    assert response.json()["owner"] == updated_playlist["owner"]
    assert response.json()["songs"] == updated_playlist["songs"]


def test_update_playlist_not_found_fails(mongo_test_empty):
    updated_playlist = {"name": "updated_name", "owner": "updated_owner", "songs": ["updated_song"]}
    response = client.put("/playlists/{}".format(str(TEST_PLAYLIST["_id"])), json=updated_playlist)
    assert response.status_code == 404


def test_delete_playlist(mongo_test):
    response = client.delete("/playlists/{}".format(TEST_PLAYLIST["_id"]))
    assert response.status_code == 204
    response_get = client.get("/playlists/{}".format(TEST_PLAYLIST["_id"]))
    assert response_get.status_code == 404


def test_delete_playlist_not_found_fails(mongo_test_empty):
    response = client.delete("/playlists/{}".format(TEST_PLAYLIST["_id"]))
    assert response.status_code == 404


def test_get_invalid_id_fails(mongo_test):
    response_get = client.get("/playlists/{}".format("123"))
    assert response_get.status_code == 400