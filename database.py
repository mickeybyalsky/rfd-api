import os
from pymongo import MongoClient

client = MongoClient(f"mongodb+srv://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSSWORD')}!@rfd-api.jdl8vta.mongodb.net/?retryWrites=true&w=majority")

user_db = client.user_db
user_collection = user_db["user_collection"]

# user_db = client.user_db
post_db = client.post_db
post_collection = post_db.post_collection

comment_db = client.comment_db
comment_collection = comment_db.comment_collection

# Access the "user_collection" and "post_collection" within their respective databases
# user_collection = user_db.user_collection