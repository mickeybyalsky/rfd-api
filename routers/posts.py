from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query, status
from auth import get_current_active_user
from models import PostInDB, PostUpdate, User, CreatePostRequest
from fastapi.responses import JSONResponse
from bson import ObjectId
from pymongo.collection import ReturnDocument
from datetime import datetime
from database import db

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)

# _id is a ObjectId type and we need JSON


def id_to_string(post):
    post["id"] = str(post["_id"])
    del post["_id"]
    return post


def id_to_string_comment(comment):
    comment["id"] = str(comment["_id"])
    del comment["_id"]
    return comment


@router.post("/",
             summary="Create a post",
             status_code=status.HTTP_201_CREATED,
             description="Create a new deal thread.",
             responses={403: {"description": "You are banned from creating posts."}, 500: {"description": "Post not created"}, 200: {"description": "Post created"}}
             )
async def create_post(post: CreatePostRequest,
                      current_user: User = Depends(get_current_active_user)):

    # check if user is banned, and if user is banned, raise an exception
    if current_user["user_role"] == "banned":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are banned from creating posts.")

    # Convert CreatePostRequest to PostInDB
    new_post = PostInDB(
        post_title=post.post_title,
        post_description=post.post_description,
        post_product_category=post.post_product_category,
        post_link_to_deal=post.post_link_to_deal,
        post_deal_expiry=post.post_deal_expiry,
        post_sale_price=post.post_sale_price,
        post_retailer=post.post_retailer,
        post_votes=0,
        post_timestamp=str(datetime.now()),
        post_author=current_user["username"],
        post_views=0,
        users_who_downvoted=[],
        users_who_upvoted=[],
        post_comments_count=0,
        bought_count=0
    )

    # insert the new post into the database
    post_result = db["posts"].insert_one(new_post.model_dump())

    # if the post was successfully created, return the post data
    if post_result.acknowledged:
        created_post = db["posts"].find_one(
            {"_id": post_result.inserted_id})  # get the post data
        # convert the _id to a string
        created_post['_id'] = str(created_post['_id'])
        db["users"].update_one({"username": current_user["username"]},
                               {"$inc": {"user_post_count": 1}}
                               )  # increment the user's post count

        # return the post data
        return JSONResponse(content={"message": f"Post {created_post['_id']} created",
                                     "post_data": created_post})

    # if the post was not created, raise an exception
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Post not created")


@router.get("/",
            summary="Read all posts",
            response_model_by_alias=False,
            description="Retrive all posts.",
            responses={404: {"description": "Users or Posts not found"}}
            )
async def get_all_posts():
    posts = list(db['posts'].find())  # get all posts

    # if there are posts, return the posts
    if posts:
        # convert each post's _id to a string
        output = [id_to_string(post) for post in posts]
        return JSONResponse(content={"posts": output})
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No posts found.")  # if there are no posts, raise an exception


@router.get("",
            summary="Read posts with filters",
            description="Retrieve posts with filter for post author.",
            responses={404: {"description": "Users or Posts not found"}}
            )
async def get_posts_filtered(username: str = Query(None, description="Optional. The post author to filter posts"),
                             retailer: str = Query(
                                 None, description="Optional. The retailer to filter posts"),
                             category: str = Query(
                                 None, description="Optional. The category to filter posts")
                             ):

    filter_params = {}  # create a dictionary to store the filter parameters

    # if a username is provided, check if the user exists
    if username:
        user_exists = db["users"].find_one({"username": username})
        if not user_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found.")  # if the user does not exist, raise an exception
        # if the user exists, add the user to the filter parameters
        filter_params["post_author"] = username

    # if a retailer is provided, add the retailer to the filter parameters
    if retailer:
        filter_params["post_retailer"] = retailer

    # if a category is provided, add the category to the filter parameters
    if category:
        filter_params["post_product_category"] = category

    # get the posts that match the filter parameters
    posts_result = db["posts"].find(filter_params)

    # if there are no posts that match the filter parameters, raise an exception
    if db["posts"].count_documents(filter_params) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No posts found for the given filters.")

    # convert the _id to a string for each post
    output = [id_to_string(post) for post in posts_result]

    # return the posts
    return JSONResponse(content={"Posts for the query": output},
                        status_code=status.HTTP_200_OK)


@router.get("/{post_id}",
            summary="Read a post",
            response_model_by_alias=False,
            description="Retrive a post by the post_id",
            response_model=PostInDB,
            responses={404: {"description": "Post not found"}, 400: {"description": "Invalid post_id format"}})
async def get_post(post_id: str = Path(title="RS", description="The ID of the post you would like to view"), examples=["60f1b9b3b3b3b3b3b3b3b3b", "60f1b9b3b3b3b3b3b3b3b3b"]):
    # check if the post_id is a valid ObjectId
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid post_id format. It must be a valid ID.")

    # find the post by the post_id and increment the post_views by 1
    post = db["posts"].find_one_and_update({"_id": ObjectId(post_id)},
                                           {"$inc": {"post_views": 1}})
    # get the comments for the post
    comments = db["comments"].find({"comment_post_id": post_id})

    # new dictionary to store the response data
    response_data = {}

    if post:
        response_data["post"] = id_to_string(post)  # set the post data

    # if there are comments, convert the _id to a string for each comment
    if db["comments"].count_documents({"comment_post_id": post_id}) > 0:
        comments = [id_to_string_comment(comment) for comment in comments]
        response_data["comments"] = comments  # set the comments data

    # if there is response data, return the response data
    if response_data:
        return JSONResponse(content={post_id: response_data},
                            status_code=status.HTTP_200_OK)

    # if there is no response data, raise an exception
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Post {post_id} not found.")


@router.put("/{post_id}",
            summary="Update a post",
            response_model_by_alias=False,
            description="Update a post by the post_id.",
            responses={404: {"description": "Post not found"}, 400: {"description": "Invalid post_id format or No valid fields to update."}, 403: {
                "description": "You are not authorized to update this post."}}
            )
async def update_post(post_id: str = Path(description="The ID of the post you would like to update"),
                      post_data: PostUpdate = Body(...,
                                                   description="The post data to update"),
                      current_user: User = Depends(get_current_active_user)):

    # check if the post_id is a valid ObjectId
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid post_id format. It must be a valid ID.")

    # find the post by the post_id
    existing_post = db["posts"].find_one({"_id": ObjectId(post_id)})
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            # if the post does not exist, raise an exception
                            detail=f"Post {post_id} not found.")

    # check if the current user is the author of the post
    if existing_post["post_author"] != current_user["username"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            # if the user is not the author of the post, raise an exception
                            detail="You are not authorized to update this post.")

    # create a dictionary of the fields to update
    update_data = {k: v for k, v in post_data.model_dump(
        by_alias=True).items() if v is not None}

    # if there are no fields to update, raise an exception
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No valid fields to update.")

    # if there are fields to update, update the post
    if len(update_data) >= 1:
        update_result = db["posts"].find_one_and_update({"_id": ObjectId(post_id)},
                                                        {"$set": update_data},
                                                        return_document=ReturnDocument.AFTER,
                                                        ) # set the updated fields and return the updated document
        
        # if the post was updated, return the updated post
        if update_result:
            update_result["_id"] = str(update_result["_id"]) # set _id to a string
            return JSONResponse(content={f"Post {update_result["_id"]} updated ": update_result},
                                status_code=status.HTTP_200_OK) # return the updated post

    # if the post was not updated, raise an exception
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Post {post_id} not found")


@router.delete("/{post_id}",
               summary="Delete a post",
               response_model_by_alias=False,
               status_code=status.HTTP_204_NO_CONTENT,
               description="Retrive a user by the username",
               responses={404: {"description": "Post not found"}, 400: {"description": "Invalid post_id format"}, 403: {
                   "description": "You are not authorized to update this post."}}
               )
async def delete_post(post_id: str = Path(description="The ID of the post you would like to remove"),
                      current_user: User = Depends(get_current_active_user)):

    # check if the post_id is a valid ObjectId
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid post_id format. It must be a valid ID.")

    # find the post by the post_id
    existing_post = db["posts"].find_one({"_id": ObjectId(post_id)})

    # if the post does not exist, raise an exception
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post {post_id} not found.")

    # check if the current user is the author of the post
    if existing_post["post_author"] != current_user["username"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to delete this post.") # if the user is not the author of the post, raise an exception

    # if the user is the author of the post, delete the post
    result = db["posts"].delete_one({"_id": ObjectId(post_id)})

    # if the post was deleted, return a message
    if result.deleted_count == 1:
        db["users"].update_one({"username": current_user["username"]},
                               {"$inc": {"user_post_count": -1}}
                               ) # decrement the user's post count
        return JSONResponse(content={"message": f"Post {post_id} removed."},
                            status_code=status.HTTP_200_OK) # return a message


@router.post("/{post_id}/upvote",
             summary="Upvote a post",
             response_model_by_alias=False,
             description="Upvote a post by the post_id",
             status_code=status.HTTP_200_OK,
             responses={404: {"description": "Post not found"}, 400: {
                 "description": "Invalid post_id format or Cannot vote on your own post"}}
             )
async def upvote_post(post_id: str = Path(description="The ID of the post to upvote"),
                      current_user: User = Depends(get_current_active_user)):
    # check if the post_id is a valid ObjectId
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid post_id format. It must be a valid ID")

    user = current_user["username"]  # create an alias

    # find the post by the post_id
    existing_post = db["posts"].find_one({"_id": ObjectId(post_id)})

    # if the post does not exist, raise an exception
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found.")

    # Raise exception because you cannot vote on own post
    if existing_post["post_author"] == current_user["username"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot vote on your own post!")

    # user not in upvoted and not in downvoted -> add 1 to upvote
    if user not in existing_post["users_who_upvoted"] and user not in existing_post["users_who_downvoted"]:
        result = db["posts"].update_one(
            {"_id": ObjectId(post_id)},
            {
                "$inc": {"post_votes": 1},
                "$push": {"users_who_upvoted": user}
            }
        )# add 1 to the post_votes and add the user to the users_who_upvoted array
        
        # Return message if upvote was successful
        if result.modified_count == 1:
            return JSONResponse(content={"message": f"Post {post_id} upvoted."},
                                status_code=status.HTTP_200_OK)

    # user in downvoted and not in upvoted -> remove from down, add to up and add 2 (1 to cancel downvote, 1 for upvote)
    if user not in existing_post["users_who_upvoted"] and user in existing_post["users_who_downvoted"]:
        result = db["posts"].update_one(
            {"_id": ObjectId(post_id)},
            {
                "$inc": {"post_votes": 2},
                "$pull": {"users_who_downvoted": user},
                "$push": {"users_who_upvoted": user}
            }
        ) # add 2 to the post_votes, remove the user from the users_who_downvoted array and add the user to the users_who_upvoted array
        
        # Return message if upvote was successful
        if result.modified_count == 1:
            return JSONResponse(content={"message": f"Post {post_id} upvoted."},
                                status_code=status.HTTP_200_OK)
    
    # if user already upvoted the post, raise an exception
    if user in existing_post["users_who_upvoted"] and user not in existing_post["users_who_downvoted"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You already upvoted this post!")
    
    # increment the post's author reputation by 1
    db["users"].update_one(
        {"username": existing_post["post_author"]},
        {"$inc": {"user_reputation": 1}},
    )

@router.post("/{post_id}/downvote",
             summary="Downvote a post",
             response_model_by_alias=False,
             description="Downvote a post by the post_id",
             status_code=status.HTTP_200_OK,
             responses={404: {"description": "Post not found"}, 400: {
                 "description": "Invalid post_id format or Cannot vote on your own post"}}
             )
async def downvote_post(post_id: str = Path(description="The ID of the post to downvote"),
                        current_user: User = Depends(get_current_active_user)):
    # check if the post_id is a valid ObjectId
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid post_id format. It must be a valid ID")

    user = current_user["username"]  # create an alias

    # find the post by the post_id
    existing_post = db["posts"].find_one({"_id": ObjectId(post_id)}) 

    # if the post does not exist, raise an exception
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found.")

    # cannot vote on own post, so return an exception
    if existing_post["post_author"] == current_user["username"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot vote on your own post!")

    # user not in upvoted and not in downvoted -> add -1 to votes
    if user not in existing_post["users_who_upvoted"] and user not in existing_post["users_who_downvoted"]:
        result = db["posts"].update_one(
            {"_id": ObjectId(post_id)},
            {
                "$inc": {"post_votes": -1},
                "$push": {"users_who_downvoted": user}
            }
        ) # add -1 to the post_votes and add the user to the users_who_downvoted array
        
        # return message if downvote was successful
        if result.modified_count == 1:
            return JSONResponse(content={"message": f"Post {post_id} downvoted."},
                                status_code=status.HTTP_200_OK)

    # user in upvoted and not in downvoted -> remove from up, add to downvoted and add -2 (1 to downvote, 1 to cancel upvote)
    if user not in existing_post["users_who_downvoted"] and user in existing_post["users_who_upvoted"]:
        result = db["posts"].update_one(
            {"_id": ObjectId(post_id)},
            {
                "$inc": {"post_votes": -2},
                "$pull": {"users_who_upvoted": user},
                "$push": {"users_who_downvoted": user}
            }
        ) # add -2 to the post_votes, remove the user from the users_who_upvoted array and add the user to the users_who_downvoted array
        
        # return message if downvote was successful
        if result.modified_count == 1:
            return JSONResponse(content={"message": f"Post {post_id} downvoted."},
                                status_code=status.HTTP_200_OK)
    
    # if user already downvoted the post, raise an exception
    if user in existing_post["users_who_downvoted"] and user not in existing_post["users_who_upvoted"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You already downvoted this post!")
    
    # decrement the post's author reputation by 1
    db["users"].update_one(
        {"username": existing_post["post_author"]},
        {"$inc": {"user_reputation": -1}},
    )
