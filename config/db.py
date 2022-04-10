import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_USER = os.getenv("MONGODB_USER")
MONGODB_PASSWD = os.getenv("MONGODB_PASSWD")

_client = pymongo.MongoClient("mongodb+srv://{}:{}@spotifiuby.8cw9h.mongodb.net/myFirstDatabase?retryWrites=true&w"
                              "=majority".format(MONGODB_USER, MONGODB_PASSWD))

conn = _client.prod
