import pytest
from bson import ObjectId
import datetime
from main import app
from fastapi.testclient import TestClient
from config.db import conn

TEST_ARTIST = {
    "_id": ObjectId("625c9dcd232be00e5f827f6a"),
    "name": "test band",
    "user_id": "user@test.com",
    "subscription_level": 0,
    "date_created": datetime.datetime.today(),
}

TEST_ARTIST_2 = {
    "_id": ObjectId("625c9dcd232be00e5f827f6b"),
    "name": "test band 2",
    "user_id": "user2@test.com",
    "subscription_level": 0,
    "date_created": datetime.datetime.today(),
}

client = TestClient(app)


@pytest.fixture()
def mongo_test_empty():
    conn.artists.delete_many({})


@pytest.fixture()
def mongo_test(mongo_test_empty):
    conn.artists.insert_one(TEST_ARTIST)


def test_get_all_artists_empty(mongo_test_empty):
    response = client.get("/artists")
    assert response.status_code == 200
    assert response.json() == []


def test_create_artist_without_user_fails(mongo_test):
    artist = {'name': TEST_ARTIST['name']}
    response = client.post("/artists", json=artist)
    assert response.status_code == 400


def test_create_artist(mongo_test_empty):
    artist = {'name': TEST_ARTIST['name']}
    response = client.post("/artists", json=artist, headers={'x-user-id': TEST_ARTIST['user_id']})
    assert response.status_code == 201
    assert len(response.json()) > 0
    response.json()["name"] = TEST_ARTIST["name"]
    response.json()["user_id"] = TEST_ARTIST["user_id"]


def test_get_all_artists(mongo_test_empty):
    artist = {'name': TEST_ARTIST['name']}
    for i in range(10):
        user_id = f'user{i}@test.com'
        client.post("/artists", json=artist, headers={'x-user-id': user_id})
    response = client.get("/artists")
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_find_artist(mongo_test_empty):
    test_artist1 = {"name": "The Beatles"}
    user_id_1 = "test1@test.com"
    test_artist2 = {"name": "The Rolling Stones"}
    user_id_2 = "test2@test.com"
    client.post("/artists", json=test_artist1, headers={'x-user-id': user_id_1})
    client.post("/artists", json=test_artist2, headers={'x-user-id': user_id_2})
    response1 = client.get("/artists", params="q=the")
    assert len(response1.json()) == 2
    response2 = client.get("/artists", params="q=beatles")
    assert len(response2.json()) == 1
    response2 = client.get("/artists", params="q=stones")
    assert len(response2.json()) == 1
    response2 = client.get("/artists", params="q=floyd")
    assert len(response2.json()) == 0


def test_get_artist_not_found(mongo_test):
    artist_id = "625c9dcd232be00e5f827f7b"
    response = client.get("/artists/{}".format(artist_id))
    assert response.status_code == 404
    assert response.json() == {"detail": "Artist {} not found".format(artist_id)}


def test_get_artist(mongo_test):
    response = client.get("/artists/{}".format(str(TEST_ARTIST["_id"])))
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["date_created"]
    del json_response["date_created"]
    expected_response = TEST_ARTIST.copy()
    expected_response['id'] = str(expected_response['_id'])
    del expected_response["_id"]
    del expected_response["date_created"]
    assert json_response == expected_response


def test_update_artist(mongo_test):
    updated_artist = {"name": "updated_name"}
    response = client.put("/artists/{}".format(str(TEST_ARTIST["_id"])), json=updated_artist,
                          headers={'x-user-id': TEST_ARTIST['user_id']})
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()["name"] == updated_artist["name"]


def test_update_artist_not_found_fails(mongo_test_empty):
    updated_artist = {"name": "updated_name"}
    response = client.put("/artists/{}".format(str(TEST_ARTIST["_id"])), json=updated_artist,
                          headers={'x-user-id': TEST_ARTIST['user_id']})
    assert response.status_code == 404


def test_delete_artist(mongo_test):
    response = client.delete("/artists/{}".format(TEST_ARTIST["_id"]))
    assert response.status_code == 204
    response_get = client.get("/artists/{}".format(TEST_ARTIST["_id"]))
    assert response_get.status_code == 404


def test_delete_artist_not_found_fails(mongo_test_empty):
    response = client.delete("/artists/{}".format(TEST_ARTIST["_id"]))
    assert response.status_code == 404


def test_get_invalid_id_fails(mongo_test):
    response_get = client.get("/artists/{}".format("123"))
    assert response_get.status_code == 400
