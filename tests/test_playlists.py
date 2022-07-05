import pytest
from bson import ObjectId
import datetime
from main import app
from fastapi.testclient import TestClient
from config.db import conn

client = TestClient(app)

TEST_SONG_1 = {
    "_id": ObjectId("625c9dcd232be00e5f827f6b"),
    "status": "active",
    "name": "test",
    "artists": ["test"],
    "date_created": datetime.datetime.today(),
    "date_uploaded": None
}

TEST_SONG_2 = {
    "_id": ObjectId("625c9dcd232be00e5f827f6c"),
    "status": "active",
    "name": "test",
    "artists": ["test"],
    "date_created": datetime.datetime.today(),
    "date_uploaded": None
}

TEST_SONG_3 = {
    "_id": ObjectId("625c9dcd232be00e5f827f6d"),
    "status": "active",
    "name": "test",
    "artists": ["test"],
    "date_created": datetime.datetime.today(),
    "date_uploaded": None
}

TEST_PLAYLIST = {
    "_id": ObjectId("625c9dcd232be00e5f827f6a"),
    "name": "test_name",
    "owner": "test_user",
    "songs": [
        str(TEST_SONG_1["_id"]),
        str(TEST_SONG_2["_id"])
    ],
    "date_created": datetime.datetime.today(),
}


@pytest.fixture()
def mongo_test_empty():
    conn.playlists.delete_many({})
    conn.songs.delete_many({})


@pytest.fixture()
def mongo_test_songs(mongo_test_empty):
    conn.songs.insert_one(TEST_SONG_1)
    conn.songs.insert_one(TEST_SONG_2)
    conn.songs.insert_one(TEST_SONG_3)


@pytest.fixture()
def mongo_test_full(mongo_test_empty, mongo_test_songs):
    conn.playlists.insert_one(TEST_PLAYLIST)


def test_get_all_playlists_empty(mongo_test_empty):
    response = client.get("/playlists")
    assert response.status_code == 200
    assert response.json() == []


def test_create_playlist(mongo_test_full):
    test_playlist = {"name": "test", "songs": [str(TEST_SONG_1["_id"]), str(TEST_SONG_2["_id"])]}
    response = client.post("/playlists", json=test_playlist, headers={"x-user-id": TEST_PLAYLIST["owner"]})
    assert response.status_code == 201
    assert len(response.json()) > 0
    assert response.json()["name"] == test_playlist["name"]
    assert response.json()["songs"] == test_playlist["songs"]
    assert response.json()["owner"] == TEST_PLAYLIST["owner"]


def test_get_all_playlists(mongo_test_songs):
    test_playlist = {"name": "test", "songs": [str(TEST_SONG_1["_id"]), str(TEST_SONG_2["_id"])]}
    for i in range(10):
        client.post("/playlists", json=test_playlist, headers={"x-user-id": TEST_PLAYLIST["owner"]})
    response = client.get("/playlists")
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_find_playlist(mongo_test_songs):
    test_playlist1 = {
        "name": "rock nacional",
        "songs": [str(TEST_SONG_1["_id"]), str(TEST_SONG_2["_id"])]
    }
    test_playlist2 = {
        "name": "punk rock",
        "songs": [str(TEST_SONG_1["_id"]), str(TEST_SONG_2["_id"])]
    }
    client.post("/playlists", json=test_playlist1, headers={"x-user-id": TEST_PLAYLIST["owner"]})
    client.post("/playlists", json=test_playlist2, headers={"x-user-id": TEST_PLAYLIST["owner"]})
    response1 = client.get("/playlists", params="q=rock")
    assert len(response1.json()) == 2
    response2 = client.get("/playlists", params="q=nacional")
    assert len(response2.json()) == 1
    response2 = client.get("/playlists", params="q=punk")
    assert len(response2.json()) == 1
    response2 = client.get("/playlists", params="q=jazz")
    assert len(response2.json()) == 0


def test_get_playlist_not_found(mongo_test_songs):
    playlist_id = "625c9dcd232be00e5f827f7b"
    response = client.get("/playlists/{}".format(playlist_id))
    assert response.status_code == 404
    assert response.json() == {"detail": "Playlist {} not found".format(playlist_id)}


def test_get_playlist(mongo_test_full):
    response = client.get("/playlists/{}".format(str(TEST_PLAYLIST["_id"])))
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["date_created"]
    del json_response["date_created"]
    expected_response = TEST_PLAYLIST.copy()
    expected_response['id'] = str(expected_response['_id'])
    expected_response['cover'] = None
    del expected_response["_id"]
    del expected_response["date_created"]
    assert json_response == expected_response


def test_add_song(mongo_test_full):
    new_songs = [str(TEST_SONG_3["_id"])]
    response = client.post("/playlists/{}".format(str(TEST_PLAYLIST["_id"])), json={"songs": new_songs},
                           headers={"x-user-id": TEST_PLAYLIST["owner"]})
    assert response.status_code == 200
    json_response = response.json()
    expected_songs = TEST_PLAYLIST["songs"].copy()
    expected_songs.extend(new_songs)
    assert json_response["songs"] == expected_songs


def test_add_song_not_found_to_playlist_fails(mongo_test_empty):
    new_songs = [str(TEST_SONG_3["_id"])]
    response = client.put("/playlists/{}".format(str(TEST_PLAYLIST["_id"])), json={'songs': new_songs})
    assert response.status_code == 404


def test_add_song_to_playlist_not_found_fails(mongo_test_songs):
    new_songs = [str(TEST_SONG_3["_id"])]
    response = client.put("/playlists/{}".format(str(TEST_PLAYLIST["_id"])), json={'songs': new_songs})
    assert response.status_code == 404


def test_delete_song(mongo_test_full):
    response = client.delete("/playlists/{}/delete/{}".format(str(TEST_PLAYLIST["_id"]),
                                                              str(TEST_PLAYLIST["songs"][0])),
                             headers={"x-user-id": TEST_PLAYLIST["owner"]})
    assert response.status_code == 200
    json_response = response.json()
    expected_songs = TEST_PLAYLIST["songs"].copy()[1:]
    assert json_response["songs"] == expected_songs


def test_update_playlist(mongo_test_full):
    updated_playlist = {
        "name": "updated_name",
        "owner": "updated_owner",
        "songs": ["625c9dcd232be00e5f827f6d"]
    }
    response = client.put("/playlists/{}".format(str(TEST_PLAYLIST["_id"])), json=updated_playlist)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()["name"] == updated_playlist["name"]
    assert response.json()["owner"] == updated_playlist["owner"]
    assert response.json()["songs"] == updated_playlist["songs"]


def test_update_playlist_not_found_fails(mongo_test_empty):
    updated_playlist = {"name": "updated_name"}
    response = client.put("/playlists/{}".format(str(TEST_PLAYLIST["_id"])), json=updated_playlist)
    assert response.status_code == 404


def test_delete_playlist(mongo_test_full):
    response = client.delete("/playlists/{}".format(TEST_PLAYLIST["_id"]))
    assert response.status_code == 204
    response_get = client.get("/playlists/{}".format(TEST_PLAYLIST["_id"]))
    assert response_get.status_code == 404


def test_delete_playlist_not_found_fails(mongo_test_empty):
    response = client.delete("/playlists/{}".format(TEST_PLAYLIST["_id"]))
    assert response.status_code == 404


def test_get_invalid_id_fails(mongo_test_full):
    response_get = client.get("/playlists/{}".format("123"))
    assert response_get.status_code == 400
