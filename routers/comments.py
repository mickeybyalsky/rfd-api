from datetime import datetime
from auth import get_current_active_user
from models import CommentBase, CommentInDB, UpdateComment, User
from fastapi import APIRouter, Depends, Path, Body, HTTPException, status
from database import comment_collection, post_collection, user_collection
from schemas import list_serial_comment, individual_serial_comment, list_serial_post
from bson import ObjectId
from fastapi.responses import JSONResponse
from pymongo.collection import ReturnDocument

router = APIRouter(
    tags=['Comments'],
)

@router.post("/api/v1/{post_id}/comments",
            summary="Create a comment",
            description="Create a comment for the provided post_id",
            response_model_by_alias=False,
            status_code=status.HTTP_201_CREATED
        )
async def create_comment(new_comment: CommentBase,
                         post_id: str,
                         current_user: User = Depends(get_current_active_user)
                         ):

    if ObjectId.is_valid(post_id):
        # if post is a valid post in the db
        post = post_collection.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Post does not exist. Comment must be created for an existing post.")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid post_id format. It must be a valid ObjectId.")  

    new_comment = CommentInDB(**new_comment.dict(),
                              comment_post_id = post_id,
                              comment_author=current_user.username,
                              comment_votes=0,
                              comment_timestamp= str(datetime.now())
                              )
    
    comment_result = comment_collection.insert_one(dict(new_comment))

    if comment_result.acknowledged:
        created_comment = comment_collection.find_one(
            {"_id": comment_result.inserted_id}
        )

        created_comment['_id'] = str(created_comment['_id'])

        return JSONResponse(content={"message": f"Comment {created_comment['_id']} created", 
                                     "comment_data": created_comment})

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                        detail="Comment not created")
 
@router.get("/api/v1/comments/{comment_id}",
            summary="Read a comment",
            description="Retrive a comment object by the comment_id.",
            response_model_by_alias=False,
            )
async def get_comment(comment_id: str = Path(description="The ID of the commment you'd like to view")):
   if not ObjectId.is_valid(comment_id):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                           detail="Invalid comment_id format. It must be a valid ObjectId")
    
   comment = comment_collection.find_one({"_id": ObjectId(comment_id)})
   comment["_id"] = str(comment["_id"])
   if comment:
      return JSONResponse(content=comment, 
                          status_code=status.HTTP_200_OK)
    
   raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                       detail="Comment not found.")

@router.get("/api/v1/comments/",
            summary="Read comments by post and/or user",
            description="Retrive all comments by the provided filter(s), or returns all comments if no parameter's provided.",
            response_model_by_alias=False,
            )
async def get_comments_filtered(username: str = None, 
                                post_id: str = None):
    filter_params = {}

    if username:
        user =  user_collection.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail="User not found.")
        filter_params["comment_author"] = username

    if post_id:
        if not ObjectId.is_valid(post_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Invalid post_id format. It must be a valid ObjectId.")
        post = post_collection.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Post not found.")
        filter_params["comment_post_id"] = str(post_id)

    comments = comment_collection.find(filter_params)

    if comments.count() > 0:
        comments_result = list_serial_comment(comments)
        return JSONResponse(content={f"Comments for the query {filter_params} ":comments_result}, 
                            status_code=status.HTTP_200_OK)
    else:
        all_comments = comment_collection.find()
        all_comments_result = list_serial_comment(all_comments)
        return JSONResponse(content={f"No filters provided. All commnents were returned ":all_comments_result}, 
                            status_code=status.HTTP_200_OK)

@router.put("/api/v1/comments/{comment_id}",
              summary="Update a Comment",
              description="Updates a comment object by the comment_id and provided request body.",
              response_model_by_alias=False,
              )
async def update_comment(comment_id: str, 
                         current_user: User = Depends(get_current_active_user),
                         comment_data: UpdateComment = Body(..., description="The comment data to update")):
    
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid comment_id format. It must be a valid ObjectId.")
    
    existing_comment = comment_collection.find_one({"_id": ObjectId(comment_id)})

    if not existing_comment: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Comment {comment_id} not found.")

    if existing_comment["comment_author"] != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to update this comment.")

    comment_data = {k: v for k, v in comment_data.model_dump(by_alias=True).items() if v}

    if not comment_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No valid fields to update.")
    
    if len(comment_data) >= 1:
        update_result = comment_collection.find_one_and_update({"_id": ObjectId(comment_id)}, 
                                                            {"$set": comment_data}, 
                                                            return_document=ReturnDocument.AFTER,
                                                            )

        if update_result:
            update_result["_id"] = str(update_result["_id"])
            return JSONResponse(content=update_result, 
                                status_code=status.HTTP_200_OK)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Comment {comment_id} not found.")
    
@router.delete("/api/v1/comments/{comment_id}",
               summary="Delete a comment",
               response_model_by_alias=False,
               description="Delete a comment object by the comment_id",
               status_code=status.HTTP_204_NO_CONTENT
               )
async def delete_comment(comment_id: str = Path(description="The ObjectID of the comment you'd like to remove"),
                         current_user: User = Depends(get_current_active_user)):
   
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Invalid comment_id format. It must be a valid ObjectId.")

    existing_comment = comment_collection.find_one({"_id": ObjectId(comment_id)})
    
    if not existing_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Comment {comment_id} not found.")
    
    if existing_comment["comment_author"] != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to delete this comment.")
    
    result = comment_collection.delete_one({"_id": ObjectId(comment_id)})
    
    if result.deleted_count == 1:
        return JSONResponse(content={"message": f"Comment {comment_id} removed."},
                            status_code=status.HTTP_200_OK)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Comment {comment_id} not found.")

@router.post("/api/v1/comments/{comment_id}/upvote",
             summary="Upvote a comment",
             response_model_by_alias=False,
             description="Upvote a comment object based on the comment_id",
             status_code=status.HTTP_200_OK
             )
async def upvote_comment(comment_id: str = Path(description="The ID of the commment to upvote"),
                         current_user: User = Depends(get_current_active_user)):
    
    if not ObjectId.is_valid(comment_id):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                          detail="Invalid comment_id format. It must be a valid ObjectId")
    
    user = current_user.username # create an alias 

    existing_comment = comment_collection.find_one({"_id": ObjectId(comment_id)})
    
    if not existing_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Comment not found.")
    
    # cannot vote on own comment!
    if existing_comment["comment_author"] == current_user.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot vote on your own comment!")

    # user not in upvoted and not in downvoted -> add 1 to upvote
    if user not in existing_comment["users_who_upvoted"] and user not in existing_comment["users_who_downvoted"]:
        result = comment_collection.update_one(
                                            {"_id": ObjectId(comment_id)},
                                            {
                                                "$inc": {"comment_votes": 1},
                                                "$push": {"users_who_upvoted": user}
                                            }
                                            )
        if result.modified_count == 1:
            return JSONResponse(content=f"Comment {comment_id} upvoted!",
                                status_code=status.HTTP_200_OK)
    
    # user in downvoted and not in upvoted -> remove from down, add to up and add 2 (1 to cancel downvote, 1 for upvote)
    if user not in existing_comment["users_who_upvoted"] and user in existing_comment["users_who_downvoted"]:
        result = comment_collection.update_one(
                                            {"_id": ObjectId(comment_id)},
                                            {
                                                "$inc": {"comment_votes": 2},
                                                "$pull": {"users_who_downvoted": user},
                                                "$push": {"users_who_upvoted": user}
                                            }
                                            )
        if result.modified_count == 1:
            return JSONResponse(content=f"Comment {comment_id} upvoted!",
                                status_code=status.HTTP_200_OK)

    if user in existing_comment["users_who_upvoted"] and user not in existing_comment["users_who_downvoted"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You already upvoted this comment!")

@router.post("/api/v1/comments/{comment_id}/downvote",
             summary="Downvote a comment",
             response_model_by_alias=False,
             description="Downvote a comment object based on the comment_id",
             status_code=status.HTTP_200_OK,
             )
async def downvote_comment(comment_id: str = Path(description="The ID of the commment to upvote"),
                           current_user: User = Depends(get_current_active_user)):
    
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid comment_id format. It must be a valid ObjectId")
    
    user = current_user.username # create an alias

    existing_comment = comment_collection.find_one({"_id": ObjectId(comment_id)})

    if not existing_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Comment not found.")
    
    #cannot vote on own post!
    if existing_comment["comment_author"] == current_user.username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot vote on your own post!")
    
    # user not in upvoted and not in downvoted -> add -1 to votes
    if user not in existing_comment["users_who_upvoted"] and user not in existing_comment["users_who_downvoted"]:
        result = comment_collection.update_one(
                                            {"_id": ObjectId(comment_id)},
                                            {
                                                "$inc": {"comment_votes": -1},
                                                "$push": {"users_who_upvoted": user}
                                            }
                                            )
        if result.modified_count == 1:
            return JSONResponse(content=f"Comment {comment_id} downvoted", 
                                status_code=status.HTTP_200_OK)
    
    # user in upvoted and not in downvoted -> remove from up, add to downvoted and add -2 (1 to downvote, 1 to cancel upvote)
    if user not in existing_comment["users_who_downvoted"] and user in existing_comment["users_who_upvoted"]:
        result = comment_collection.update_one(
                                            {"_id": ObjectId(comment_id)},
                                            {
                                                "$inc": {"comment_votes": -2},
                                                "$pull": {"users_who_upvoted": user},
                                                "$push": {"users_who_downvoted": user}
                                            }
                                            )
        if result.modified_count == 1:
            return JSONResponse(content=f"Comment {comment_id} downvoted.", 
                                status_code=status.HTTP_200_OK)

    if user in existing_comment["users_who_downvoted"] and user not in existing_comment["users_who_upvoted"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="You already downvoted this comment!")
