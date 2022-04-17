import pymongo
import pymongo_inmemory
import os
from dotenv import load_dotenv
import firebase_admin

load_dotenv()

# Mongo
if os.getenv("CURRENT_ENVIRONMENT") == "production":
    _client = pymongo.MongoClient(
        "mongodb+srv://{}:{}@spotifiuby.8cw9h.mongodb.net/myFirstDatabase?retryWrites=true&w""=majority".format(
            os.getenv("MONGODB_USER"), os.getenv("MONGODB_PASSWD")))
    conn = _client.prod
else:
    _client = pymongo_inmemory.MongoClient()
    conn = _client.testdb

# Firebase
BUCKET = "spotifiuby-3c9fe.appspot.com"
default_app = firebase_admin.initialize_app()
