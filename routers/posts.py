from fastapi import APIRouter, Depends, HTTPException, Path, Body, status
import pytz
from auth import get_current_active_user
from models import PostIn, PostInDB, PostUpdate, UpdateComment, User
from database import post_collection, comment_collection 
from schemas import list_serial_comment, list_serial_post, individual_serial_post
from fastapi.responses import JSONResponse
from bson import ObjectId
from pymongo.collection import ReturnDocument
from datetime import datetime

router = APIRouter(
    prefix='/api/v1/posts',
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
async def create_post(post: PostIn,
                      current_user: User = Depends(get_current_active_user)):
    
    new_post = PostInDB(
                        **post.dict(),
                        post_votes=0,
                        post_timestamp = str(datetime.now()),
                        post_author = current_user.username,
                        post_views = 0,
                        users_who_downvoted=[],
                        users_who_upvoted=[]
                        )

    post_result = post_collection.insert_one(dict(new_post))
    
    if post_result.acknowledged:
        created_post = post_collection.find_one({"_id": post_result.inserted_id})
        created_post['_id'] = str(created_post['_id'])                                  
        return JSONResponse(content={"message": f"Post {created_post['_id']} created", 
                                     "post_data": created_post})
    
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        detail="Post not created")

@router.get("/",
            summary="Read all posts",
            response_model_by_alias=False,
            description="Retrive all posts."
            )
async def get_all_posts():
    posts = list_serial_post(post_collection.find())
    if posts:   
        return JSONResponse(content={"posts": posts})
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail="No posts found.")

@router.get("/{post_id}",
            summary="Read a post",
            response_model_by_alias=False,
            description="Retrive a post by the post_id"
            )
async def get_post(post_id: str = Path(description="The ID of the post you would like to view")):
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid post_id format. It must be a valid ObjectId.")

    post = post_collection.find_one_and_update({"_id": ObjectId(post_id)}, 
                                               {"$inc": {"post_views": 1}})
    print(post)
    comments = comment_collection.find({"comment_post_id": post_id})
    
    response_data = {}

    if post:
        response_data["post"] = individual_serial_post(post)

    if comments.count() > 0:
        comments =  list_serial_comment(comments)
        response_data["comments"] = comments

    if response_data:
        return JSONResponse(content={post_id: response_data},
                            status_code=status.HTTP_200_OK)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Post {post_id} not found.")

@router.get("/{username}",
            summary="Read all posts by a specific user",
            include_in_schema=False,
            description="Retrive all posts by the provided username"
            )
async def get_all_posts_by_user(username: str = Path(description="The username of the author whose posts you would like to get.")):
    posts = list_serial_post(post_collection.find({"username": username}))
    if posts: 
        return JSONResponse(content={"message": f"Posts for user {username}", 
                                     "posts": posts})
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail="No posts found.")


@router.put("/{post_id}",
              summary="Update a post",
              response_model_by_alias=False,
              description="Update a post by the post_id."
              )
async def update_post(post_id: str, 
                      post_data: PostUpdate = Body(..., description="The post data to update"),
                      current_user: User = Depends(get_current_active_user)):
    
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid post_id format. It must be a valid ObjectId.")
    
    existing_post = post_collection.find_one({"_id": ObjectId(post_id)})
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post {post_id} not found.")

    if existing_post["post_author"] != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to update this post.")

    update_data = {k: v for k, v in post_data.model_dump(by_alias=True).items() if v}

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="No valid fields to update.")
    
    if len(update_data) >= 1:
        update_result = post_collection.find_one_and_update({"_id": ObjectId(post_id)}, 
                                                        {"$set": update_data}, 
                                                        return_document=ReturnDocument.AFTER,
                                                        )
        if update_result:
            update_result["_id"] = str(update_result["_id"])
            return JSONResponse(content=update_result, 
                                status_code=status.HTTP_200_OK)
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Post {post_id} not found")
    
@router.delete("/{post_id}",
               summary="Delete a post",
               response_model_by_alias=False,
               status_code=status.HTTP_204_NO_CONTENT,
               description="Retrive a user by the username"
               )
async def delete_post(post_id: str = Path(description="The ObjectID of the post you would like to remove"),
                      current_user: User = Depends(get_current_active_user)):
    
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid post_id format. It must be a valid ObjectId.")

    existing_post = post_collection.find_one({"_id": ObjectId(post_id)})

    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post {post_id} not found.")
    
    if existing_post["post_author"] != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not authorized to delete this post.")
    
    result = post_collection.delete_one({"_id": ObjectId(post_id)})
    
    if result.deleted_count == 1:
        return JSONResponse(content={"message": f"Post {post_id} removed."}, 
                            status_code=status.HTTP_200_OK)

@router.post("/{post_id}/upvote",
             summary="Upvote a post",
             response_model_by_alias=False,
             description="Upvote a post by the post_id",
             status_code=status.HTTP_200_OK
             )
async def upvote_post(post_id: str = Path(description="The ID of the post to upvote"),
                      current_user: User = Depends(get_current_active_user)):
    if not ObjectId.is_valid(post_id):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                          detail="Invalid post_id format. It must be a valid ObjectId")
    
    user = current_user.username # create an alias 

    existing_post = post_collection.find_one({"_id": ObjectId(post_id)})
    
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found.")
    
    # cannot vote on own post!
    if existing_post["post_author"] == current_user.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot vote on your own post!")

    # user not in upvoted and not in downvoted -> add 1 to upvote
    if user not in existing_post["users_who_upvoted"] and user not in existing_post["users_who_downvoted"]:
        result = post_collection.update_one(
                                            {"_id": ObjectId(post_id)},
                                            {
                                                "$inc": {"post_votes": 1},
                                                "$push": {"users_who_upvoted": user}
                                            }
                                            )
        if result.modified_count == 1:
            return JSONResponse(content=f"post {post_id} upvoted", 
                                status_code=status.HTTP_200_OK)
    
    # user in downvoted and not in upvoted -> remove from down, add to up and add 2 (1 to cancel downvote, 1 for upvote)
    if user not in existing_post["users_who_upvoted"] and user in existing_post["users_who_downvoted"]:
        result = post_collection.update_one(
                                            {"_id": ObjectId(post_id)},
                                            {
                                                "$inc": {"post_votes": 2},
                                                "$pull": {"users_who_downvoted": user},
                                                "$push": {"users_who_upvoted": user}
                                            }
                                            )
        if result.modified_count == 1:
            return JSONResponse(content=f"post {post_id} upvoted", 
                                status_code=status.HTTP_200_OK)

    if user in existing_post["users_who_upvoted"] and user not in existing_post["users_who_downvoted"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="You already upvoted this post!")

@router.post("/{post_id}/downvote",
             summary="Downvote a post",
             response_model_by_alias=False,
             description="Downvote a post by the post_id",
             status_code=status.HTTP_200_OK
             )
async def downvote_post(post_id: str = Path(description="The ID of the post to downvote"),
                        current_user: User = Depends(get_current_active_user)):
    
    if not ObjectId.is_valid(post_id):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                          detail="Invalid post_id format. It must be a valid ObjectId")
    
    user = current_user.username # create an alias

    existing_post = post_collection.find_one({"_id": ObjectId(post_id)})

    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Post not found.")
    
    #cannot vote on own post!
    if existing_post["post_author"] == current_user.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Cannot vote on your own post!")
    

    # user not in upvoted and not in downvoted -> add -1 to votes
    if user not in existing_post["users_who_upvoted"] and user not in existing_post["users_who_downvoted"]:
        result = post_collection.update_one(
                                            {"_id": ObjectId(post_id)},
                                            {
                                                "$inc": {"post_votes": -1},
                                                "$push": {"users_who_upvoted": user}
                                            }
                                            )
        if result.modified_count == 1:
            return JSONResponse(content=f"Post {post_id} downvoted", 
                                status_code=status.HTTP_200_OK)
    
    # user in upvoted and not in downvoted -> remove from up, add to downvoted and add -2 (1 to downvote, 1 to cancel upvote)
    if user not in existing_post["users_who_downvoted"] and user in existing_post["users_who_upvoted"]:
        result = post_collection.update_one(
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
                            detail="You already upvoted this post!")
