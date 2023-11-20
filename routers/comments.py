from models import Comment, UpdateComment
from fastapi import APIRouter, Path, Body, HTTPException, status
from database import comment_collection, post_collection, user_collection
from schemas import list_serial_comment, individual_serial_comment, list_serial_post
from bson import ObjectId
from fastapi.responses import JSONResponse
from pymongo.collection import ReturnDocument


''' COMMENT FUNCTIONS
CREATE comments for a post
READ a comment by comment
READ comments for a post
READ all comments for a user
READ all Comments
UPDATE comments
DELETE comments
upvote/downvote comments
'''

router = APIRouter(
    tags=['Comments'],
    prefix="/comments"

)

@router.post("/",
            summary="Create a comment",
            response_model_by_alias=False,
            status_code=status.HTTP_201_CREATED
        )
async def create_comment(new_comment: Comment):
    if ObjectId.is_valid(new_comment.user_id):
        # if user is a valid user in the db
        user = user_collection.find_one({"_id": ObjectId(new_comment.user_id)})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist. Comment must be created for an existing user.")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id format. It must be a valid ObjectId.")
    
    if ObjectId.is_valid(new_comment.post_id):
        # if post is a valid post in the db
        post = post_collection.find_one({"_id": ObjectId(new_comment.post_id)})
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post does not exist. Comment must be created for an existing post.")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid post_id format. It must be a valid ObjectId.")  

    new_comment = new_comment.model_dump(by_alias=True, exclude=["id"])
    comment_result = comment_collection.insert_one(new_comment)

    if comment_result.acknowledged:
        created_comment = comment_collection.find_one(
            {"_id": comment_result.inserted_id}
        )
        
        created_comment['_id'] = str(created_comment['_id'])

        return JSONResponse(content={"message": f"Comment {created_comment['_id']} created", "comment_data": created_comment})

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Comment not created")
 
@router.get("/{comment_id}",
            summary="Get a comment",
            response_model_by_alias=False,
            )
async def get_comment(comment_id: str = Path(description="The ID of the commment you'd like to view")):
   if not ObjectId.is_valid(comment_id):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid comment_id format. It must be a valid ObjectId")
    
   comment = comment_collection.find_one({"_id": ObjectId(comment_id)})

   if comment:
      comment = individual_serial_comment(comment)
      return JSONResponse(content=comment, status_code=status.HTTP_200_OK)
    
   raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

@router.get("/",
            summary="Get comments with optional filters",
            description="Retrive's all comments based on provided filter, or returns all comments if no parameter's provided",
            response_model_by_alias=False,
            )
async def get_comments_filtered(user_id: str = None, post_id: str = None):
    filter_params = {}

    if user_id:
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id format. It must be a valid ObjectId.")
        user =  user_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        filter_params["user_id"] = ObjectId(user_id)

    if post_id:
        if not ObjectId.is_valid(post_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid post_id format. It must be a valid ObjectId.")
        post = post_collection.posts.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
        filter_params["post_id"] = ObjectId(post_id)

    comments = comment_collection.find(filter_params)

    if comments:
        comments_result = list_serial_comment(comments)
        return JSONResponse(content=comments_result, status_code=status.HTTP_200_OK)

    all_comments = comment_collection.find()
    all_comments_result = list_serial_comment(all_comments)
    return JSONResponse(content=all_comments_result, status_code=status.HTTP_200_OK)

@router.put("/{comment_id}",
              summary="Update a Comment",
              response_model_by_alias=False,
              )
async def update_comment(comment_id: str, comment_data: UpdateComment = Body(..., description="The comment data to update")):
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid comment_id format. It must be a valid ObjectId.")
    
    comment_data = {k: v for k, v in comment_data.model_dump(by_alias=True).items() if v}

    if len(comment_data) >= 1:
        update_result = comment_collection.find_one_and_update({"_id": ObjectId(comment_id)}, 
                                                            {"$set": comment_data}, 
                                                            return_document=ReturnDocument.AFTER,
                                                            )

        if update_result:
            update_result["_id"] = str(update_result["_id"])
            return JSONResponse(content=update_result, status_code=status.HTTP_200_OK)
        
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comment {comment_id} not found")
    
    existing_comment = comment_collection.find_one({"_id": ObjectId(comment_id)})
    if existing_comment:
        existing_comment["_id"] = str(existing_comment["_id"])
        return existing_comment

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comment {comment_id} not found.")
    
@router.delete("/{comment_id}",
               summary="Delete a comment",
               response_model_by_alias=False,
               status_code=status.HTTP_204_NO_CONTENT
               )
async def delete_comment(comment_id: str = Path(description="The ObjectID of the comment you'd like to remove")):
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid comment_id format. It must be a valid ObjectId.")

    result = comment_collection.delete_one({"_id": ObjectId(comment_id)})
    
    if result.deleted_count == 1:
        return JSONResponse(content={"message": f"Comment {comment_id} removed."}, status_code=status.HTTP_200_OK)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comment {comment_id} not found.")

@router.put("/{comment_id}/upvote",
             summary="Upvote a comment",
             response_model_by_alias=False,
             status_code=status.HTTP_200_OK
             )
async def upvote_comment(comment_id: str = Path(description="The ID of the commment to upvote")):
    print(comment_id)
    if not ObjectId.is_valid(comment_id):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid comment_id format. It must be a valid ObjectId")
    
    comment = comment_collection.find_one({"_id": ObjectId(comment_id)})
    if comment:
        result = comment_collection.update_one(
            {"_id": ObjectId(comment_id)},
            {"$inc": {"comment_votes": 1}})
        if result.modified_count == 1:
            return JSONResponse(content=f"Comment {comment_id} upvoted", status_code=status.HTTP_200_OK)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

@router.put("/{comment_id}/downvote",
             summary="Downvote a comment",
             response_model_by_alias=False,
             status_code=status.HTTP_200_OK
             )
async def upvote_comment(comment_id: str = Path(description="The ID of the commment to upvote")):
    print(comment_id)
    if not ObjectId.is_valid(comment_id):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid comment_id format. It must be a valid ObjectId")
    
    comment = comment_collection.find_one({"_id": ObjectId(comment_id)})
    if comment:
        result = comment_collection.update_one(
            {"_id": ObjectId(comment_id)},
            {"$inc": {"comment_votes": -1}})
        if result.modified_count == 1:
            return JSONResponse(content=f"Comment {comment_id} downvoted", status_code=status.HTTP_200_OK)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")