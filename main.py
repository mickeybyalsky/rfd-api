from fastapi import Body, FastAPI, Path
import routers.users as users, routers.posts as posts, routers.comments as comments

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


