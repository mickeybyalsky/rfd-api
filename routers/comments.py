from models import Comment
from fastapi import APIRouter, Path, Body, HTTPException, status
from database import comment_collection, post_collection, user_collection
from schemas import list_serial_comment, individual_serial_comment, list_serial_post
from bson import ObjectId
from fastapi.responses import JSONResponse

comments_db = {}

''' COMMENT FUNCTIONS
CREATE comments for a post
READ a comment
READ comments for a post
READ all comments for a user
READ all Comments
UPDATE comments
DELETE comments
'''

router = APIRouter(
    tags=['Comments']
)

@router.post("/comments")
async def create_comment(new_comment: Comment):
    
    if not ObjectId.is_valid(ObjectId(new_comment.post_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid post_id format. It must be a valid ObjectId.")  
    
    post = post_collection.find_one({"_id": ObjectId(new_comment.post_id)})
    if not post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post does not exist. Comment must be created for an existing post.")

   #  if not ObjectId.is_valid(new_comment.user_id):
   #      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id format. It must be a valid ObjectId.")
    # user = user_collection.find_one({"_id": new_comment["user_id"]})
    # if not user:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist. Comment must be created for an existing post.")

    new_comment = new_comment.model_dump()
    comment_result = comment_collection.insert_one(new_comment)

    if comment_result.acknowledged:
        new_comment_id = str(comment_result.inserted_id)
        return JSONResponse(content={"message": "Comment created successfully", "comment_id": new_comment_id}, status_code=status.HTTP_201_CREATED)
    '''
    add commment to comment db and each comment will have a reference to the post id in the attribute
    '''

@router.get("/comments")
async def get_all_comments():
   comments = list_serial_comment(comment_collection.find())
   if comments:
       return comments

   raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No comments found.")
 
@router.get("/comments/{comment_id}")
async def get_comment(comment_id: str = Path(description="The ID of the commment you'd like to view")):
   if not ObjectId.is_valid(comment_id):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid comment_id format. It must be a valid ObjectId")
    
   comment = comment_collection.find_one({"_id": ObjectId(comment_id)})

   if comment:
      comment = list_serial_comment(comment)
      return JSONResponse(content=comment, status_code=status.HTTP_200_OK)
    
   raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

    # post = post_collection.find_one({"_id": ObjectId(post_id)})

    # if not post:
    #     raise HTTPException(status_code=404, detail="Post not found")
    
    # else:
    #     post = list_serial_post(post)
    #     return {"post": post}
    
    

    # if post_id not in post_db:
    #     return {"message": f"Post with UUID {post_id} not found."}
    # else:
    #     comment_id = str(len(comments_db) + 1)
    #     comments_db[comment_id] = new_comment
    #     return new_comment

    # if post_id in post_db:
    #     post = post_db[post_id]
        
    #     if post.post_comments is None:
    #         post.post_comments = []
        
    #     post.post_comments.append(new_comment)
    #     new_comment_id = str(uuid.uuid4())
    #     new_comment.comment_id = new_comment_id
    #     # post_db.get(post_id)["post_comments"][comment_id] = new_comment
    #     return {"message": f"Comment Created. UUID is {new_comment_id}"}   
    # else: 
    #     return {"message": f"Post with UUID {post_id} not found."}

@router.get("comments/{user_id}")
async def get_comment_by_user(user_id: str):
   if not ObjectId.is_valid(ObjectId(user_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id format. It must be a valid ObjectId.")  
   
   user_comments = comment_collection.find({"user_id": ObjectId(user_id)})

   user_comments = list_serial_comment(user_comments)

   return user_comments

@router.get("comments/{post_id}")
async def get_comment_by_post(post_id: str):
     pass
# @router.get("/comments")
# async def read_all_comments():
#     pass

# @router.get("/posts/{post_id}/comments", tags=["Comments"])
# async def read_post_comments(post_id: str):
#     if post_id in post_db:
#         filtered_comments = [comment for comment in comments_db.values() if comment.post_id == post_id]
#         return filtered_comments
#     else:
#         return {"message": f"Post with UUID {post_id} not found."}
#     # if post_id in post_db:
#     #     post = post_db[post_id]
#     #     if post.post_comments:
#     #         return post.post_comments
#     #     else:
#     #         return {"message": f"Post with UUID {post_id} has no comments."}
#     # else:
#     #     return {"message": f"Post with UUID {post_id} not found."}

# @router.get("/posts/{post_id}/comments/{comment_id}", tags=["Comments"])
# async def read_comment(post_id: str, comment_id: str = Path(description="The ID of the comment you'd like to view")):
#     comment = comments_db.get(comment_id)
#     if comment:
#         return comment
#     else:
#         return {"message": f"Comment with UUID {comment_id} not found."}

# @router.patch("/posts/{post_id}/comments/{comment_id}", tags=["Comments"])
# async def update_comment(post_id: str, comment_id: str, comment_data: Comment = Body(..., description="The post data to update")):
#     if post_id in post_db:
#         # Get the existing post data from the database
#         existing_post = post_db[post_id]
        
#         if comment_id in existing_post["post_comments"]: 
#             existing_comment = existing_post["post_comments"][comment_id]
            
#             if comment_data.comment_body:
#                 existing_comment["comment_body"] = comment_data.comment_body

#         # Return the updated user data
#         return existing_post

#     return {"message": f"Post with UUID {post_id} found."}

# @router.delete("/comments/{comment_id}", tags = ["Comments"])
# async def delete_comment(post_id: str, comment_id: str = Path(description="The UUID of the comment you'd like to remove")):
#     # comment_to_delete = post_db[post_id]["post_comments"][comment_id]
#     if comment_id in comments_db:
#         del comment_id
#         return {"message": f"Comment with UUID {comment_id} successfully deleted."} 
#     else:
#         return {"message": f"Comment not found."}
