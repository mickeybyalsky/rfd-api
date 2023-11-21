from fastapi import APIRouter, HTTPException, Path, Body, status
from models import Post, UpdatePost
from database import post_collection, comment_collection 
from schemas import list_serial_comment, list_serial_post, individual_serial_post
from fastapi.responses import JSONResponse
from bson import ObjectId
from pymongo.collection import ReturnDocument

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
            response_model_by_alias=False,
            status_code=status.HTTP_201_CREATED
        )
async def create_post(post: Post):
    new_post = post.model_dump(by_alias=True, exclude=["id"])
    post_result = post_collection.insert_one(new_post)
    
    if post_result.acknowledged:
        created_post = post_collection.find_one(
            {"_id": post_result.inserted_id}
        )
    
        created_post['_id'] = str(created_post['_id'])                                  

        return JSONResponse(content={"message": f"Post {created_post['_id']} created", "post_data": created_post})
    
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Post not created")

@router.get("/",
            summary="Get all posts",
            response_model_by_alias=False
            )
async def get_all_posts():
    posts = list_serial_post(post_collection.find())
    if posts:   
        return posts
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found.")

@router.get("/{post_id}",
            summary="Get a post",
            response_model_by_alias=False,
            )
async def get_post(post_id: str = Path(description="The ID of the post you'd like to view")):
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid post_id format. It must be a valid ObjectId.")

    post = post_collection.find_one({"_id": ObjectId(post_id)})
    comments = comment_collection.find({"post_id": post_id})
    
    response_data = {}

    if post:
        response_data["post"] = individual_serial_post(post)

    if comments.count() > 0:
        comments =  list_serial_comment(comments)
        response_data["comments"] = comments

    if response_data:
        return JSONResponse(content=response_data, status_code=status.HTTP_200_OK)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {post_id} not found.")

@router.put("/{post_id}",
              summary="Update a post",
              response_model_by_alias=False,
              )
async def update_post(post_id: str, post_data: UpdatePost = Body(..., description="The post data to update")):
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid post_id format. It must be a valid ObjectId.")
    
    post_data = {k: v for k, v in post_data.model_dump(by_alias=True).items() if v}

    if len(post_data) >= 1:
        update_result = post_collection.find_one_and_update({"_id": ObjectId(post_id)}, 
                                                            {"$set": post_data}, 
                                                            return_document=ReturnDocument.AFTER,
                                                            )

        if update_result:
            update_result["_id"] = str(update_result["_id"])
            return JSONResponse(content=update_result, status_code=status.HTTP_200_OK)
        
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {post_id} not found")
    existing_post = post_collection.find_one({"_id": ObjectId(post_id)})

    if existing_post:
        existing_post["_id"] = str(existing_post["_id"])
        return existing_post

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {post_id} not found.")
    
@router.delete("/{post_id}",
               summary="Delete a post",
               response_model_by_alias=False,
               status_code=status.HTTP_204_NO_CONTENT
               )
async def delete_post(post_id: str = Path(description="The ObjectID of the post you'd like to remove")):
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid post_id format. It must be a valid ObjectId.")

    result = post_collection.delete_one({"_id": ObjectId(post_id)})
    
    if result.deleted_count == 1:
        return JSONResponse(content={"message": f"Post {post_id} removed."}, status_code=status.HTTP_200_OK)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {post_id} not found.")

@router.put("/{post_id}/upvote",
             summary="Upvote a post",
             response_model_by_alias=False,
             status_code=status.HTTP_200_OK
             )
async def upvote_post(post_id: str = Path(description="The ID of the post to upvote")):
    print(post_id)
    if not ObjectId.is_valid(post_id):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid post_id format. It must be a valid ObjectId")
    
    post = post_collection.find_one({"_id": ObjectId(post_id)})
    if post:
        result = post_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$inc": {"post_votes": 1}})
        if result.modified_count == 1:
            return JSONResponse(content=f"post {post_id} upvoted", status_code=status.HTTP_200_OK)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found.")

@router.put("/{post_id}/downvote",
             summary="Downvote a post",
             response_model_by_alias=False,
             status_code=status.HTTP_200_OK
             )
async def downvote_post(post_id: str = Path(description="The ID of the commment to upvote")):
    print(post_id)
    if not ObjectId.is_valid(post_id):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid post_id format. It must be a valid ObjectId")
    
    post = post_collection.find_one({"_id": ObjectId(post_id)})
    if post:
        result = post_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$inc": {"post_votes": -1}})
        if result.modified_count == 1:
            return JSONResponse(content=f"post {post_id} downvoted", status_code=status.HTTP_200_OK)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found.")