from fastapi import Body, FastAPI, Path
import routers.users as users, routers.posts as posts, routers.comments as comments

#TODO: Add .get() everywhere
#TODO: Make seperate files for each schema
#TODO: Front Page of docs
#TODO: https://fastapi.tiangolo.com/tutorial/bigger-applications/

#TODO: python3 -m uvicorn main:app --reload
#TODO: MONGODB
#TODO: ADMIN controls (ban user/override delete/update?)
#TODO: Auth for each user (each person can only update/delete their own post)
#TODO: Check if delete method actually deletes
#TODO: Fix patch/put method
#TODO: Enum for stores/retailers https://fastapi.tiangolo.com/tutorial/path-params/#create-an-enum-class
#TODO: Add categories
#TODO: change UUID parameter from str to UUID everywhere
#TODO: HTTP responses, field for each input, examples in the docs, do some validation on input (greater t, less t)

''' USER FUNCTIONS
CREATE user
READ user
READ all users 
UPDATE user
DELETE user
'''
''' POST FUNCTIONS
CREATE post
READ post
READ all posts
UPDATE post
DELETE post
'''
''' COMMENT FUNCTIONS
CREATE comments
READ a comment
READ comments for a post
READ all Comments
UPDATE comments
DELETE comments
'''
''' SUBFORUM FUNCTIONS
CREATE subforum
READ subforum
UPDATE subforum
DELETE subforum
'''

# CREATE retailer
# READ retailer
# UPDATE retailer
# DELETE retailer

app = FastAPI()
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)


