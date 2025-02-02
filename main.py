from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
import routers.users as users, routers.posts as posts, routers.comments as comments, auth
from database import db


description = """
A recreation to the RedFlagDeals experience, made for fun and to explore the world of REST API's.
<br>
Inspired by a few dabs at the real RFD by me and my friends, such as "How do I downvote a comment?", I said I can make it happen.
<br>
I've spent loads of hours on the site in the past year and scored some awsome deals myself. I wanted to learn about REST API's and wondered what better way to do it by trying to recreate a site I loved.
<br>
<br>
This RESTful API serves to recreate a fully functional backend of RedFlagDeals, by having users, posts, and comments and all the interaction that comes along with it, on a MongoDB mock database. 
<br>
Have some fun by creating a user, then creating a post or reading some posts, and maybe leave a comment on an exisiting post!
<br>
<br>
**Steps**: To use the endpoints, expand the dropdown of an endpoint, press "Try it out", fill in any fields if applicable and hit execute!
<br>
<br>
**Using Authorized Endpoints:**: You will first need to register a user, then use the authorize button to log into that user. Then you are all set to use all the endpoints!
<br>
<br>
<br>
Made with Python, FastAPI and MongoDB. Hosted on AWS EC2

## Users 

You will be able to:

* [Create/Register a user](#/default/create_user_api_v1_users_register_post)
* [Read all users](#/Users/get_all_users_api_v1_users__get)
* [Read your user](#/Users/get_user_api_v1_users_me_get)
* [Read a user](#/Users/get_user_api_v1_users__username__get)
* [Update a users](#/Users/update_user_api_v1_users__username__put)
* [Delete a user](#/Users/delete_user_api_v1_users__username__delete)

## Posts

You will be able to:

* [Read all posts]
* [Create a post]
* [Read posts with optional filters]
* [Read a post]
* [Update a post]
* [Delete a post]
* [Upvote a post]
* [Downvote a post]

## Comments

You will be able to:

* Create a comment
* Read a comment
* Read comments filtered by post and/or user
* Update a comment
* Delete a comment
* Upvote a comment
* Downvote a comment

## Misc

You will be able to: 

* Read API statistics

## Roadmap

* Administrator/Moderator functions (Delete posts/comments of other users and ban/temporarily disabling users)
* Enumerate merchants when creating or searching for posts for a more cohesive experience
* Adding discussion forums
* Better experience for replying to comments
"""

app = FastAPI(
    title="RedFlagDeals REST API",
    description=description,
    version="1.1",
    contact={
        "name": "Mickey Byalsky",
        "url": "https://www.linkedin.com/in/mickeybyalsky/",
        "email": "mickeybyalsky@gmail.com",
    }
)

# include the router for auth
app.include_router(auth.router)

# include the router for user routes
app.include_router(users.router, prefix="/api/v1")

# include the router for post routes
app.include_router(posts.router, prefix="/api/v1")

# include the router for comment routes
app.include_router(comments.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/stats",
         summary="Read API statistics",
         )
async def get_metrics():
    metrics = {}

    metrics["document_counts"] = {
        "user_count" : db["users"].count_documents({}),
        "post_count" : db["posts"].count_documents({}),
        "comment_count" : db["comments"].count_documents({})
    }

    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_post_views": {"$sum": "$post_views"},
                "total_post_upvotes": {"$sum": {"$size": {"$ifNull": ["$users_who_upvoted", []]}}},
                "total_post_downvotes": {"$sum": {"$size": {"$ifNull": ["$users_who_downvoted", []]}}}
            }
        }
    ]   

    temp = list(db["posts"].aggregate(pipeline))
    
    metrics["total_view_count_of_posts"] = temp[0]["total_post_views"] if temp else 0

    metrics["vote_counts"] = {
        "total_post_upvotes_count": temp[0]["total_post_upvotes"] if temp else 0,
        "total_post_downvotes_count": temp[0]["total_post_downvotes"] if temp else 0,
    }
    
    return JSONResponse(content={"metrics": metrics}, status_code=status.HTTP_200_OK)