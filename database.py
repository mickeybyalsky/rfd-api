import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(f"mongodb+srv://{os.environ.get('MONGODB_USERNAME')}:{os.environ.get('MONGODB_PASSWORD')}@rfd-api.jdl8vta.mongodb.net/?retryWrites=true&w=majority")

db = client["rfd-api"]


