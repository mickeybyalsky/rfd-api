from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import JSONResponse
from auth import get_current_user
from database import db
from models import User


router = APIRouter(
    tags=["Admin"],
)

def id_to_string(comment):
    comment["comment_id"] = str(comment["_id"])
    del comment["_id"]
    return comment

@router.get("/admin",
            responses={403: {"description": "You do not have permission to perform this action"}})
async def admin(current_user: User = Depends(get_current_user)):
    
    # Check if the user is an admin
    if current_user["user_role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action")
    
    return {"message": "Welcome to the admin panel!"}

@router.get("/admins",
            summary="Get all admins",
            description="Get all admins",
            response_description="List of all admins",
            response_model=List[str],
            responses={200: {"description": "List of all admins"}},
            )
async def get_admins():
    # Find all users with the role of admin
    admins = db["users"].find({"user_role": "admin"}, projection={"hashed_password": 0})
    
    # Convert the ObjectId to a string
    admins = [id_to_string(admin) for admin in admins]
    
    return JSONResponse(content=admins, status_code=status.HTTP_200_OK)

@router.post("/admin/add_admin/{username}",
             summary="Promote a user to an admin",
             description="Promote a user to an admin",
             responses={403: {"description": "You do not have permission to perform this action"}, 404: {"description": "User not found"}},
             )
async def add_admin(username: str = Path(..., description="The username of the user to promote to admin"),
                    current_user: User = Depends(get_current_user)): 
    
    # Check if the user is an admin
    if current_user["user_role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action")
    
    # Find the user in the database
    user = db["users"].find_one({"username": username})
    
    # If the user is not found, raise an HTTPException
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Update the user's role to admin
    db["users"].update_one({"username": username}, {"$set": {"user_role": "admin"}})
    
    # Return a message
    return {"message": f"{username} is now an admin"}

@router.post("/admin/remove_admin/{username}",
             summary="Remove admin privileges from a user",
             description="Remove admin privileges from a user",
             responses={403: {"description": "You do not have permission to perform this action"}, 404: {"description": "User not found"}},
            )
async def remove_admin(username: str = Path(..., description="The username of the user to remove admin privileges from"),
                       current_user: User = Depends(get_current_user)):
    
    # Check if the user is an admin
    if current_user["user_role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action")
    
    # Find the user in the database
    user = db["users"].find_one({"username": username})
    
    # If the user is not found, raise an HTTPException
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Update the user's role to user
    db["users"].update_one({"username": username}, {"$set": {"user_role": "user"}})
    
    # Return a message
    return {"message": f"{username} is no longer an admin"}

@router.delete("/admin/delete_user/{username}",
             summary="Delete a user",
             description="Delete a user",
             responses={403: {"description": "You do not have permission to perform this action"}, 404: {"description": "User not found"}},
             )
async def delete_user(username: str = Path(..., description="The username of the user to delete"), 
                      current_user: User = Depends(get_current_user)):
    
    # Check if the user is an admin
    if current_user["user_role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action")
    
    # Find the user in the database
    result = db["users"].find_one({"username": username})
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Delete the user from the database
    db["users"].delete_one({"username": username})
    
    # Return a message
    return {"message": f"{username} has been deleted"}

@router.delete("/admin/delete_comment/{comment_id}",
             summary="Delete a comment",
             description="Delete a comment",
             responses={403: {"description": "You do not have permission to perform this action"}, 404: {"description": "User not found"}},
             )
async def delete_comment(comment_id: str = Path(..., description="The ID of the comment to delete"),
                            current_user: User = Depends(get_current_user)):
    
    # Check if the user is an admin
    if current_user["user_role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action")
    
    # Find the comment in the database
    result = db["comments"].find_one({"_id": ObjectId(comment_id)})
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    
    # Delete the comment from the database
    db["comments"].delete_one({"_id": ObjectId(comment_id)})
    
    # Return a message
    return {"message": f"Comment {comment_id} has been deleted"}

@router.delete("/admin/delete_post/{post_id}",
             summary="Delete a post",
             description="Delete a post",
             responses={403: {"description": "You do not have permission to perform this action"}, 404: {"description": "User not found"}},
)
async def delete_post(post_id: str = Path(..., description="The ID of the post to delete"),
                        current_user: User = Depends(get_current_user)):
    
    # Check if the user is an admin
    if current_user["user_role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action")
    
    # Find the post in the database
    result = db["posts"].find_one({"_id": ObjectId(post_id)})
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    # Delete the post from the database
    db["posts"].delete_one({"_id": ObjectId(post_id)})
    
    # Return a message
    return {"message": f"Post {post_id} has been deleted"}

@router.post("/admin/ban_user/{username}",
                summary="Ban a user",
                description="Ban a user",
                responses={403: {"description": "You do not have permission to perform this action"}, 404: {"description": "User not found"}},
                )
async def ban_user(username: str = Path(..., description="The username of the user to ban"),
                    current_user: User = Depends(get_current_user)):
    
    # Check if the user is an admin
    if current_user["user_role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to perform this action")
    
    # Find the user in the database
    result = db["users"].find_one({"username": username})
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Update the user's role to banned
    db["users"].update_one({"username": username}, {"$set": {"user_role": "banned"}})
    
    # Return a message
    return {"message": f"{username} has been banned"}
    
    