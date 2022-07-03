import pymongo
import os
from dotenv import load_dotenv
import firebase_admin
from google.cloud import storage
import pymongo_inmemory

from config.mock_mongo import BucketMock

load_dotenv()

test = os.getenv("CURRENT_ENVIRONMENT") != "production"

# Mongo
if not test:
    _client = pymongo.MongoClient(
        f"mongodb+srv://{os.getenv('MONGODB_USER')}:{os.getenv('MONGODB_PASSWD')}@backend-songs.yhk0y.mongodb.net"
        f"/backend-songs?retryWrites=true&w=majority")
    conn = _client.prod
else:
    _client = pymongo_inmemory.MongoClient()
    conn = _client.testdb

# Firebase
if not test:
    BUCKET = "spotifiuby-3c9fe.appspot.com"
    default_app = firebase_admin.initialize_app()
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET)
else:
    bucket = BucketMock()
