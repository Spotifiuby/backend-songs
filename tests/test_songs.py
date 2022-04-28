import pytest
from bson import ObjectId
from main import app
from fastapi.testclient import TestClient
from config.db import conn

client = TestClient(app)


@pytest.fixture()
def mongo_test_empty():
    conn.songs.delete_many({})


@pytest.fixture()
def mongo_test(mongo_test_empty):
    conn.songs.insert_one({
        "_id": ObjectId("625c9dcd232be00e5f827f6a"),
        "status": "active",
        "name": "test",
        "artists": ["test"]
    })


def test_get_all_songs_empty(mongo_test_empty):
    response = client.get("/songs")
    assert response.status_code == 200
    assert response.json() == []


def test_create_song(mongo_test):
    response = client.post("/songs", json={"name": "test", "artists": ["test"]})
    assert response.status_code == 201
    assert len(response.json()) > 0
    response.json()["name"] = "test"


def test_get_all_songs(mongo_test_empty):
    for i in range(10):
        client.post("/songs", json={"name": "test", "artists": ["test"]})
    response = client.get("/songs")
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_get_song_not_found(mongo_test):
    response = client.get("/songs/625c9dcd232be00e5f827f7b")
    assert response.status_code == 404
    assert response.json() == {"detail": "Song 625c9dcd232be00e5f827f7b not found"}


def test_get_song(mongo_test):
    response = client.get("/songs/625c9dcd232be00e5f827f6a")
    assert response.status_code == 200
    assert response.json() == {'artists': ['test'], 'id': '625c9dcd232be00e5f827f6a', 'name': 'test',
                               'status': 'active'}
