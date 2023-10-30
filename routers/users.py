import uuid
from fastapi import APIRouter, HTTPException, Path, Body, status
from models import User
from database import user_collection
from schemas import list_serial_user, individual_serial_user
from bson import ObjectId

router = APIRouter(
    prefix='/users',
    tags=['Users']
)
'''
post_result = post_collection.insert_one(post_dict)
    
    if post_result.acknowledged:
        new_post_id = str(post_result.inserted_id)
'''
@router.post("/")
async def create_user(user: User):
    user_dict = user.model_dump()
    user_result = user_collection.insert_one(user_dict)
    
    if user_result.acknowledged:
        new_user_id = str(user_result.inserted_id)
        return {"message": "User created successfully", "user_id": new_user_id}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User was not inserted to database")

@router.get("/")
async def read_users():
    users = list_serial_user(user_collection.find())
    if users:   
        return users
    
    raise HTTPException(status_code=404, detail="No users found.")

@router.get("/{user_id}")
async def read_user(user_id: str = Path(description="The ID of the user you'd like to view")):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id format. It must be a valid ObjectId.")
       
    # Use find_one to retrieve the user by ObjectId
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    
    if user:
        user = individual_serial_user(user)
        return {"user": user}

    raise HTTPException(status_code=404, detail="User not found")
     
@router.patch("/{user_id}")
async def update_user(user_id: str, user_data: User = Body(..., description="The user data to update")):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id format. It must be a valid ObjectId.")
    user_query = {"_id": ObjectId(user_id)}  # Assuming "_id" is the user's unique identifier in your MongoDB collection

    existing_user = user_collection.find_one(user_query)

    if existing_user:
        # Update the user's attributes if provided in the request
        update_data = {}

        if user_data.user_display_name:
            update_data["user_display_name"] = user_data.user_display_name
        if user_data.user_email:
            update_data["user_email"] = user_data.user_email
        if user_data.user_location:
            update_data["user_location"] = user_data.user_location

        # Perform the update
        user_collection.update_one(user_query, {"$set": update_data})

        # Return the updated user data
        updated_user = user_collection.find_one(user_query)
        if updated_user:
            updated_user["_id"] = str(updated_user["_id"])

            # Return the response with the updated user data
            return {"message": f"User with ObjectID {user_id} updated", "user_data": updated_user}
        else:
            return {"message": f"User with ObjectID {user_id} not found."}
    else:
        return {"message": f"User with ObjectID {user_id} not found."}

@router.delete("/{user_id}")
def delete_user(user_id: str = Path(description="The ObjectID of the user you'd like to remove")):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id format. It must be a valid ObjectId.")

    result = user_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 1:
        # return {"message": f"User with ObjectID {user_id} successfully deleted."} 
        # message deleted
        return status.HTTP_204_NO_CONTENT
    
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ObjectID {user_id} not found.")
    