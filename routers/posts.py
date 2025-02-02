from fastapi import APIRouter, Depends, HTTPException, Path, Body, Query, status
from auth import get_current_active_user
from models import PostInDB, PostUpdate, User, CreatePostRequest
from schemas import list_serial_comment, list_serial_post, individual_serial_post
from fastapi.responses import JSONResponse
from bson import ObjectId
from pymongo.collection import ReturnDocument
from datetime import datetime
from database import db

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)


''' POST FUNCTIONS
CREATE post
READ post
READ all posts
UPDATE post
DELETE post
get posts by category
get posts by user
get posts by retailer 
'''

@router.post("/",
            summary="Create a post",
            status_code=status.HTTP_201_CREATED,
            description="Create a new deal thread."
        )
async def create_post(post: CreatePostRequest,
                      current_user: User = Depends(get_current_active_user)):
    if current_user["user_role"] == "banned":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are banned from creating posts.")
    new_post = PostInDB(
                        post_title = post.post_title,
                        post_description = post.post_description, 
                        post_product_category = post.post_product_category,
                        post_link_to_deal = post.post_link_to_deal,
                        post_deal_expiry = post.post_deal_expiry,
                        post_sale_price = post.post_sale_price,
                        post_retailer = post.post_retailer,
                        post_votes=0,
                        post_timestamp = str(datetime.now()),
                        post_author = current_user["username"],
                        post_views = 0,
                        users_who_downvoted=[],
                        users_who_upvoted=[],
                        post_comments_count=0,
                        bought_count=0
                        )

    post_result = db["posts"].insert_one(new_post.model_dump())
    
    if post_result.acknowledged:
        created_post = db["posts"].find_one({"_id": post_result.inserted_id})
        created_post['_id'] = str(created_post['_id'])          
        db["users"].update_one({"username": current_user["username"]},
                                    {"$inc": {"user_post_count": 1}}
        )  
                  
        return JSONResponse(content={"message": f"Post {created_post['_id']} created", 
                                     "post_data": created_post})
    
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        detail="Post not created")

# _id is a ObjectId type and we need JSON
def id_to_string(post):
    post["id"] = str(post["_id"])
    del post["_id"]
    return post

def id_to_string_comment(comment):
    comment["id"] = str(comment["_id"])
    del comment["_id"]
    return comment

@router.get("/",
            summary="Read all posts",
            response_model_by_alias=False,
            description="Retrive all posts.",
            responses={404: {"description": "Users or Posts not found"}}
            )
async def get_all_posts():
    posts = list(db['posts'].find())
    if posts:
        output = [id_to_string(post) for post in posts]
        return JSONResponse(content={"posts": output})
    else:      
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail="No posts found.")

@router.get("",
            summary="Read posts with filters",
            description="Retrieve posts with filter for post author.",
            responses={404: {"description": "Users or Posts not found"}}
            )
async def get_posts_filtered(username: str = Query(description="Optional. The post author to filter posts"),
                             retailer: str = Query(description="Optional. The retailer to filter posts"),
                             category: str = Query(description="Optional. The category to filter posts")
                             ):
    filter_params = {}
    user_exists = db["users"].find_one({"username": username})
    if not user_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="User not found.")
    else:
        users_posts =  db["posts"].find_one({"post_author": username})
        if not users_posts:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"{username} has not created any posts.")

        filter_params["post_author"] = username
        if retailer:
            filter_params["post_retailer"] = retailer
        if category:
            filter_params["post_product_category"] = category

        if db["posts"].count_documents(filter_params) > 0:
            posts_result = db["posts"].find(filter_params)
            output = [id_to_string(post) for post in posts_result]
            if filter_params:
                return JSONResponse(content={f"Posts for the query {filter_params} ": output},
                                    status_code=status.HTTP_200_OK)
            else:
                return JSONResponse(content={f"No filters provided. All posts were returned ": output },
                                    status_code=status.HTTP_200_OK)

@router.get("/{post_id}",
            summary="Read a post",
            response_model_by_alias=False,
            description="Retrive a post by the post_id",
            response_model=PostInDB,
            responses={404: {"description": "Post not found"}, 400: {"description": "Invalid post_id format"}})
async def get_post(post_id: str = Path(title="RS", description="The ID of the post you would like to view"), examples=["60f1b9b3b3b3b3b3b3b3b3b", "60f1b9b3b3b3b3b3b3b3b3b"]):
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid post_id format. It must be a valid ID.")

    post = db["posts"].find_one_and_update({"_id": ObjectId(post_id)}, 
                                               {"$inc": {"post_views": 1}})
    comments = db["comments"].find({"comment_post_id": post_id})
    
    response_data = {}

    if post:
        response_data["post"] = id_to_string(post)

    if db["comments"].count_documents({"comment_post_id": post_id}) > 0:
        comments =  [id_to_string_comment(comment) for comment in comments]
        response_data["comments"] = comments

    if response_data:
        return JSONResponse(content={post_id: response_data},
                            status_code=status.HTTP_200_OK)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Post {post_id} not found.")

# @router.get("/{username}",
#             summary="Read all posts by a specific user",
#             include_in_schema=False,
#             description="Retrive all posts by the provided username"
#             )
# async def get_all_posts_by_user(username: str = Path(description="The username of the author whose posts you would like to get.")):
#     if not db["users"].find_one({"username": username}):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        
#     posts = list_serial_post(db["posts"].find({"post_author": username}))
#     if posts: 
#         return JSONResponse(content={"message": f"Posts for user {username}", 
#                                      "posts": posts})
    
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
#                         detail="No posts found.")

@router.put("/{post_id}",
              summary="Update a post",
              response_model_by_alias=False,
              description="Update a post by the post_id.",
              responses={404: {"description": "Post not found"}, 400: {"description": "Invalid post_id format or No valid fields to update."}, 403: {"description": "You are not authorized to update this post."}}
              )
async def update_post(post_id: str = Path(description="The ID of the post you would like to update"), 
                      post_data: PostUpdate = Body(..., description="The post data to update"),
                      current_user: User = Depends(get_current_active_user)):
    
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid post_id format. It must be a valid ID.")
    
    existing_post = db["posts"].find_one({"_id": ObjectId(post_id)})
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post {post_id} not found.")

    if existing_post["post_author"] != current_user["username"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to update this post.")

    update_data = {k: v for k, v in post_data.model_dump(by_alias=True).items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="No valid fields to update.")
    
    if len(update_data) >= 1:
        update_result = db["posts"].find_one_and_update({"_id": ObjectId(post_id)}, 
                                                        {"$set": update_data}, 
                                                        return_document=ReturnDocument.AFTER,
                                                        )
        if update_result:
            update_result["_id"] = str(update_result["_id"])
            return JSONResponse(content={f"Post {update_result["_id"]} updated ": update_result },
                                status_code=status.HTTP_200_OK)
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Post {post_id} not found")
    
@router.delete("/{post_id}",
               summary="Delete a post",
               response_model_by_alias=False,
               status_code=status.HTTP_204_NO_CONTENT,
               description="Retrive a user by the username",
               responses={404: {"description": "Post not found"}, 400: {"description": "Invalid post_id format"}, 403: {"description": "You are not authorized to update this post."}}
               )
async def delete_post(post_id: str = Path(description="The ID of the post you would like to remove"),
                      current_user: User = Depends(get_current_active_user)):
    
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid post_id format. It must be a valid ID.")

    existing_post = db["posts"].find_one({"_id": ObjectId(post_id)})

    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post {post_id} not found.")
    
    if existing_post["post_author"] != current_user["username"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not authorized to delete this post.")
    
    result = db["posts"].delete_one({"_id": ObjectId(post_id)})
    
    if result.deleted_count == 1:
        db["users"].update_one({"username": current_user["username"]},
                                    {"$inc": {"user_post_count": -1}}
        )  
        return JSONResponse(content={"message": f"Post {post_id} removed."}, 
                            status_code=status.HTTP_200_OK)

@router.post("/{post_id}/upvote",
             summary="Upvote a post",
             response_model_by_alias=False,
             description="Upvote a post by the post_id",
             status_code=status.HTTP_200_OK,
             responses={404: {"description": "Post not found"}, 400: {"description": "Invalid post_id format or Cannot vote on your own post"}}
             )
async def upvote_post(post_id: str = Path(description="The ID of the post to upvote"),
                      current_user: User = Depends(get_current_active_user)):
    if not ObjectId.is_valid(post_id):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                          detail="Invalid post_id format. It must be a valid ID")
    
    user = current_user["username"] # create an alias 

    existing_post = db["posts"].find_one({"_id": ObjectId(post_id)})
    
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found.")
    
    # cannot vote on own post!
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
                                            )
        if result.modified_count == 1:
            return JSONResponse(content=f"Post {post_id} upvoted", 
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
                                            )
        if result.modified_count == 1:
            return JSONResponse(content=f"Post {post_id} upvoted", 
                                status_code=status.HTTP_200_OK)

    if user in existing_post["users_who_upvoted"] and user not in existing_post["users_who_downvoted"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="You already upvoted this post!")
    
    db["users"].update_one(
        {"username": existing_post["post_author"]},
        {"$inc": {"user_reputation": 1}},
    )
  
@router.post("/{post_id}/downvote",
             summary="Downvote a post",
             response_model_by_alias=False,
             description="Downvote a post by the post_id",
             status_code=status.HTTP_200_OK,
             responses={404: {"description": "Post not found"}, 400: {"description": "Invalid post_id format or Cannot vote on your own post"}}
             )
async def downvote_post(post_id: str = Path(description="The ID of the post to downvote"),
                        current_user: User = Depends(get_current_active_user)):
    
    if not ObjectId.is_valid(post_id):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                          detail="Invalid post_id format. It must be a valid ID")
    
    user = current_user.username # create an alias

    existing_post = db["posts"].find_one({"_id": ObjectId(post_id)})

    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Post not found.")
    
    #cannot vote on own post!
    if existing_post["post_author"] == current_user.username:
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
                                            )
        if result.modified_count == 1:
            return JSONResponse(content=f"Post {post_id} downvoted", 
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
                                            )
        if result.modified_count == 1:
            return JSONResponse(content=f"Post {post_id} downvoted.", 
                                status_code=status.HTTP_200_OK)

    if user in existing_post["users_who_downvoted"] and user not in existing_post["users_who_upvoted"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="You already downvoted this post!")

    db["users"].update_one(
        {"username": existing_post["post_author"]},
        {"$inc": {"user_reputation": -1}},
    )