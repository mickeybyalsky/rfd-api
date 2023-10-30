import uuid
from fastapi import APIRouter, HTTPException, Path, Body, status
from models import Post
from database import post_collection 
from schemas import list_serial_post, individual_serial_post
from bson import ObjectId

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)

@router.post("/")
async def create_post(post: Post):
    post_dict = post.model_dump()
    post_result = post_collection.insert_one(post_dict)
    
    if post_result.acknowledged:
        new_post_id = str(post_result.inserted_id)
        return {"message": "Post created successfully", "post_id": new_post_id}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Post was not inserted to database")

@router.get("/", status_code=status.HTTP_200_OK)
async def read_posts():
    posts = list_serial_post(post_collection.find())
    if posts:   
        return posts
    
    raise HTTPException(status_code=404, detail="No posts found.")

@router.get("/{post_id}", status_code=status.HTTP_200_OK)
async def read_post(post_id: str = Path(description="The ID of the post you'd like to view")):
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid post_id format. It must be a valid ObjectId.")

    post = post_collection.find_one({"_id": ObjectId(post_id)})

    if post:
        post = list_serial_post(post)
        return {"post": post}
    
    raise HTTPException(status_code=404, detail="Post not found")
    
@router.patch("/{post_id}")
async def update_post(post_id: str, post_data: Post = Body(..., description="The post data to update")):
    # post_query = {"_id": ObjectId(post_id)}
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid post_id format. It must be a valid ObjectId.")
    
    existing_post = post_collection.find_one({"_id": post_id})

    if existing_post:
        update_data = {}

        if post_data.post_title: 
            update_data["post_title"] = post_data.post_title
        if post_data.post_description:
            update_data["post_description"] = post_data.post_description
        if post_data.post_retailer:
            update_data["post_retailer"] = post_data.post_retailer

        post_collection.update_one({"_id": post_id}, {"$set": update_post})

        updated_post = post_collection.find_one({"_id": post_id})

        if updated_post: 
            updated_post["_id"] = updated_post["_id"]

            return {"message": f"Post with ID {post_id} updated", "post_data": updated_post}
        else:
                return {"message": f"Post with ID {post_id} not found."}
    else:
        return {"message": f"Post with ID {post_id} not found."}

@router.delete("/{post_id}")
async def delete_post(post_id: str = Path(description="The ObjectID of the post you'd like to remove")):
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=400, detail="Invalid post_id format. It must be a valid ObjectId.")

    result = post_collection.delete_one({"_id": ObjectId(post_id)})
    if result.deleted_count == 1:
        return status.HTTP_204_NO_CONTENT
    
    else:
        raise HTTPException(status_code=404, detail=f"Post with ObjectID {post_id} not found.")

    