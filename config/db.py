import pymongo
import pymongo_inmemory
import os
from dotenv import load_dotenv
import firebase_admin
from google.cloud import storage

load_dotenv()

# Mongo
if os.getenv("CURRENT_ENVIRONMENT") == "production":
    _client = pymongo.MongoClient(
        f"mongodb+srv://{os.getenv('MONGODB_USER')}:{os.getenv('MONGODB_PASSWD')}@backend-songs.yhk0y.mongodb.net"
        f"/backend-songs?retryWrites=true&w=majority")
    conn = _client.prod
else:
    _client = pymongo_inmemory.MongoClient()
    conn = _client.testdb


# Firebase
class BlobMock:
    c = ""

    def upload_from_string(self, c):
        self.c = c
        return

    def download_as_string(self):
        return self.c


class BucketMock:
    d = dict()

    def blob(self, s):
        if s in self.d:
            return self.d[s]
        b = BlobMock()
        self.d[s] = b
        return b


if os.getenv("CURRENT_ENVIRONMENT") == "production":
    BUCKET = "spotifiuby-3c9fe.appspot.com"
    default_app = firebase_admin.initialize_app()
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET)
else:
    default_app = firebase_admin.initialize_app()
    bucket = BucketMock()
