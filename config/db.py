import pymongo
import os
from dotenv import load_dotenv
import firebase_admin

load_dotenv()

# Mongo
MONGODB_USER = os.getenv("MONGODB_USER")
MONGODB_PASSWD = os.getenv("MONGODB_PASSWD")

_client = pymongo.MongoClient("mongodb+srv://{}:{}@spotifiuby.8cw9h.mongodb.net/myFirstDatabase?retryWrites=true&w"
                              "=majority".format(MONGODB_USER, MONGODB_PASSWD))

conn = _client.prod

# Firebase
BUCKET = "spotifiuby-3c9fe.appspot.com"
default_app = firebase_admin.initialize_app()
