from models import Comment
from fastapi import APIRouter, Path, Body, HTTPException
from database import comment_collection, post_collection
from schemas import list_serial_comment, individual_serial_comment, list_serial_post
from bson import ObjectId

comments_db = {}

''' COMMENT FUNCTIONS
CREATE comments for a post
READ a comment
READ comments for a post
READ all Comments
UPDATE comments
DELETE comments
'''

router = APIRouter(
    tags=['Comments']
)

@router.post("/posts/{post_id}/comments", tags=["Comments"])
async def create_comment(post_id: str, new_comment: Comment):
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid post_id format. It must be a valid ObjectId.")

    post = post_collection.find_one({"_id": ObjectId(post_id)})

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    else:
        post = list_serial_post(post)
        return {"post": post}
    
    

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

@router.get("/comments")
async def read_all_comments():
    pass

@router.get("/posts/{post_id}/comments", tags=["Comments"])
async def read_post_comments(post_id: str):
    if post_id in post_db:
        filtered_comments = [comment for comment in comments_db.values() if comment.post_id == post_id]
        return filtered_comments
    else:
        return {"message": f"Post with UUID {post_id} not found."}
    # if post_id in post_db:
    #     post = post_db[post_id]
    #     if post.post_comments:
    #         return post.post_comments
    #     else:
    #         return {"message": f"Post with UUID {post_id} has no comments."}
    # else:
    #     return {"message": f"Post with UUID {post_id} not found."}

@router.get("/posts/{post_id}/comments/{comment_id}", tags=["Comments"])
async def read_comment(post_id: str, comment_id: str = Path(description="The ID of the comment you'd like to view")):
    comment = comments_db.get(comment_id)
    if comment:
        return comment
    else:
        return {"message": f"Comment with UUID {comment_id} not found."}

@router.patch("/posts/{post_id}/comments/{comment_id}", tags=["Comments"])
async def update_comment(post_id: str, comment_id: str, comment_data: Comment = Body(..., description="The post data to update")):
    if post_id in post_db:
        # Get the existing post data from the database
        existing_post = post_db[post_id]
        
        if comment_id in existing_post["post_comments"]: 
            existing_comment = existing_post["post_comments"][comment_id]
            
            if comment_data.comment_body:
                existing_comment["comment_body"] = comment_data.comment_body

        # Return the updated user data
        return existing_post

    return {"message": f"Post with UUID {post_id} found."}

@router.delete("/comments/{comment_id}", tags = ["Comments"])
async def delete_comment(post_id: str, comment_id: str = Path(description="The UUID of the comment you'd like to remove")):
    # comment_to_delete = post_db[post_id]["post_comments"][comment_id]
    if comment_id in comments_db:
        del comment_id
        return {"message": f"Comment with UUID {comment_id} successfully deleted."} 
    else:
        return {"message": f"Comment not found."}


'''


2. **Get All Comments**:
   - **HTTP Method**: GET
   - **URL**: `/comments`
   - **Description**: Retrieve a list of all comments.

3. **Get a Specific Comment**:
   - **HTTP Method**: GET
   - **URL**: `/comments/{comment_id}`
   - **Description**: Retrieve a specific comment by its unique identifier (comment_id).

6. **Get Comments for a Specific Post**:
   - **HTTP Method**: GET
   - **URL**: `/posts/{post_id}/comments`
   - **Description**: Retrieve all comments associated with a specific post (post_id).

4. **Update a Comment**:
   - **HTTP Method**: PATCH or PUT
   - **URL**: `/comments/{comment_id}`
   - **Description**: Update an existing comment by its unique identifier.

5. **Delete a Comment**:
   - **HTTP Method**: DELETE
   - **URL**: `/comments/{comment_id}`
   - **Description**: Delete a specific comment by its unique identifier.


7. **Create a Comment for a Specific Post**:
   - **HTTP Method**: POST
   - **URL**: `/posts/{post_id}/comments`
   - **Description**: Create a new comment associated with a specific post (post_id).
'''