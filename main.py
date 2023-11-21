from fastapi import FastAPI
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

description = """
A homage to the genuine RedFlagDeals experience, made with love and inspired by countless hours spent on the real site. 
<br>
Inspired by a few dabs at the real RFD by me and my friends, such as "How do I downvote a comment?", I said I can make it happen.
<br>
I've spent loads of hours on the site in the past year and scored some awsome deals myself.
<br>
<br>
This API serves to recreate a fully functional backend of RedFlagDeals, by having users, posts, and comments and all the interaction that comes along with it, on a mock MongoDB database. 
<br>
Have some fun by creating a user, creating a post or reading some posts and maybe leave a comment on an exisiting post!
<br>
<br>
**Steps**: To use the endpoints, expand the dropdown of an endpoint, press "Try it out", fill in any fields if applicable and hit execute!
<br>
<br>
<br>
Made with Python, FastAPI and MongoDB. Hosted on AWS
## Users

You will be able to:

* Create users
* Read users
* Update users
* Delete users

## Posts

You will be able to:

* Create posts
* Read posts
* Update posts
* Delete posts

## Comments

You will be able to:

* Create comments
* Read comments
* Update comments
* Delete comments
"""

app = FastAPI(
    title="RedFlagDeals REST API",
    description=description,
    version="1.0",
    contact={
        "name": "Mickey Byalsky",
        "url": "https://www.linkedin.com/in/mickeybyalsky/",
        "email": "mickeybyalsky@gmail.com",
    },
)

app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)


