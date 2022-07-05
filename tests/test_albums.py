import pytest
from bson import ObjectId
import datetime
from fastapi.testclient import TestClient

from main import app
from config.db import conn
from tests.test_artists import TEST_ARTIST, TEST_ARTIST_2

client = TestClient(app)

TEST_SONG_1 = {
    "_id": ObjectId("625c9dcd232be00e5f827f6e"),
    "status": "active",
    "name": "test",
    "artists": [
        TEST_ARTIST['_id']
    ],
    "date_created": datetime.datetime.today(),
    "date_uploaded": None
}

TEST_SONG_2 = {
    "_id": ObjectId("625c9dcd232be00e5f827f6f"),
    "status": "active",
    "name": "test",
    "artists": [
        TEST_ARTIST['_id']
    ],
    "date_created": datetime.datetime.today(),
    "date_uploaded": None
}

TEST_SONG_3 = {
    "_id": ObjectId("625c9dcd232be00e5f827f7a"),
    "status": "active",
    "name": "test",
    "artists": [
        TEST_ARTIST['_id']
    ],
    "date_created": datetime.datetime.today(),
    "date_uploaded": None
}

TEST_ALBUM = {
    "_id": ObjectId("625c9dcd232be00e5f827f6a"),
    "name": "test_name",
    "artists": [
        TEST_ARTIST['_id']
    ],
    "songs": [
        str(TEST_SONG_1["_id"]),
        str(TEST_SONG_2["_id"])
    ],
    "year": 2022,
    "date_created": datetime.datetime.today(),
}


@pytest.fixture()
def mongo_test_empty():
    conn.albums.delete_many({})
    conn.songs.delete_many({})
    conn.artists.delete_many({})


@pytest.fixture()
def mongo_test_songs(mongo_test_empty):
    conn.artists.insert_one(TEST_ARTIST)
    conn.artists.insert_one(TEST_ARTIST_2)
    conn.songs.insert_one(TEST_SONG_1)
    conn.songs.insert_one(TEST_SONG_2)
    conn.songs.insert_one(TEST_SONG_3)


@pytest.fixture()
def mongo_test(mongo_test_empty, mongo_test_songs):
    conn.albums.insert_one(TEST_ALBUM)


def test_get_all_albums_empty(mongo_test_empty):
    response = client.get("/albums")
    assert response.status_code == 200
    assert response.json() == []


def test_find_playlist(mongo_test_songs):
    test_album1 = {
        "name": "The Wall",
        "artists": [str(TEST_ARTIST['_id'])],
        "songs": [str(TEST_SONG_1["_id"]), str(TEST_SONG_2["_id"])],
        "year": 1979
    }
    test_album2 = {
        "name": "Revolver",
        "artists": [str(TEST_ARTIST['_id'])],
        "songs": [str(TEST_SONG_1["_id"]), str(TEST_SONG_2["_id"])],
        "year": 1966
    }
    client.post("/albums", json=test_album1)
    client.post("/albums", json=test_album2)
    response1 = client.get("/albums", params="q=e")
    assert len(response1.json()) == 2
    response2 = client.get("/albums", params="q=wall")
    assert len(response2.json()) == 1
    response2 = client.get("/albums", params="q=rev")
    assert len(response2.json()) == 1
    response2 = client.get("/albums", params="q=dark")
    assert len(response2.json()) == 0


def test_create_album(mongo_test):
    test_album = {
        "name": "test",
        "artists": [str(TEST_ARTIST['_id'])],
        "songs": [str(TEST_SONG_1["_id"]), str(TEST_SONG_2["_id"])],
        "year": 1990
    }
    response = client.post("/albums", json=test_album)
    assert response.status_code == 201
    assert len(response.json()) > 0
    assert response.json()["name"] == test_album["name"]
    assert response.json()["artists"] == [str(TEST_ARTIST['_id'])]
    assert response.json()["songs"] == test_album["songs"]
    assert response.json()["year"] == test_album["year"]


def test_get_all_albums(mongo_test_songs):
    test_album = {
        "name": "test",
        "artists": [str(TEST_ARTIST['_id'])],
        "songs": [
            str(TEST_SONG_1["_id"]),
            str(TEST_SONG_2["_id"])
        ],
        "year": 1990}
    for i in range(10):
        client.post("/albums", json=test_album)
    response = client.get("/albums")
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_get_album_not_found(mongo_test):
    response = client.get("/albums/625c9dcd232be00e5f827f7b")
    assert response.status_code == 404
    assert response.json() == {"detail": "Album 625c9dcd232be00e5f827f7b not found"}


def test_get_album(mongo_test):
    response = client.get("/albums/{}".format(str(TEST_ALBUM["_id"])))
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["date_created"]
    del json_response["date_created"]
    expected_response = TEST_ALBUM.copy()
    expected_response['id'] = str(expected_response['_id'])
    expected_response['artists'] = [TEST_ARTIST['name']]
    expected_response['cover'] = None
    del expected_response["_id"]
    del expected_response["date_created"]
    assert json_response == expected_response


def test_add_song(mongo_test):
    new_song = str(TEST_SONG_3["_id"])
    response = client.put("/albums/{}/songs".format(str(TEST_ALBUM["_id"])), params={'song_id': new_song})
    assert response.status_code == 200
    json_response = response.json()
    expected_songs = TEST_ALBUM["songs"].copy()
    expected_songs.append(new_song)
    assert json_response["songs"] == expected_songs


def test_add_song_not_found_to_album_fails(mongo_test_empty):
    new_song = str(TEST_SONG_3["_id"])
    response = client.put("/albums/{}/songs".format(str(TEST_ALBUM["_id"])), params={'song_id': new_song})
    assert response.status_code == 404


def test_add_song_to_album_not_found_fails(mongo_test_songs):
    new_song = str(TEST_SONG_3["_id"])
    response = client.put("/albums/{}/songs".format(str(TEST_ALBUM["_id"])), params={'song_id': new_song})
    assert response.status_code == 404


def test_add_artist(mongo_test):
    response = client.put("/albums/{}/artists".format(str(TEST_ALBUM["_id"])),
                          params={'artist_id': TEST_ARTIST_2['_id']})
    assert response.status_code == 200
    json_response = response.json()
    expected_artists = TEST_ALBUM["artists"].copy()
    expected_artists.append(TEST_ARTIST_2['_id'])
    assert json_response["artists"] == [str(a) for a in expected_artists]


def test_add_artist_to_album_not_found_fails(mongo_test_empty):
    response = client.put("/albums/{}/artists".format(str(TEST_ALBUM["_id"])),
                          params={'artist_id': TEST_ARTIST_2['_id']})
    assert response.status_code == 404


def test_update_album(mongo_test):
    updated_album = {
        "name": "updated_name",
        "artists": [str(TEST_ARTIST["_id"])],
        "songs": [str(TEST_SONG_3["_id"])],
        "year": 2010
    }
    response = client.put("/albums/{}".format(str(TEST_ALBUM["_id"])), json=updated_album)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()["name"] == updated_album["name"]
    assert response.json()["artists"] == updated_album["artists"]
    assert response.json()["songs"] == updated_album["songs"]
    assert response.json()["year"] == updated_album["year"]


def test_update_album_not_found_fails(mongo_test_empty):
    updated_album = {"name": "updated_name"}
    response = client.put("/albums/{}".format(str(TEST_ALBUM["_id"])), json=updated_album)
    assert response.status_code == 404


def test_delete_album(mongo_test):
    response = client.delete("/albums/{}".format(TEST_ALBUM["_id"]))
    assert response.status_code == 204
    response_get = client.get("/albums/{}".format(TEST_ALBUM["_id"]))
    assert response_get.status_code == 404


def test_delete_album_not_found_fails(mongo_test_empty):
    response = client.delete("/albums/{}".format(TEST_ALBUM["_id"]))
    assert response.status_code == 404


def test_get_invalid_id_fails(mongo_test):
    response_get = client.get("/albums/{}".format("123"))
    assert response_get.status_code == 400
