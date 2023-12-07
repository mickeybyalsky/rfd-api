import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(f"mongodb+srv://{os.environ.get('MONGODB_USERNAME')}:{os.environ.get('MONGODB_PASSSWORD')}@rfd-api.jdl8vta.mongodb.net/?retryWrites=true&w=majority")

user_db = client.user_db
user_collection = user_db.user_collection

post_db = client.post_db
post_collection = post_db.post_collection

comment_db = client.comment_db
comment_collection = comment_db.comment_collection