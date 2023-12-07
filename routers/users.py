from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Path, Body, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import pytz
from models import UserOut, UserUpdate, UserIn, UserInDB
from database import user_collection
from schemas import list_serial_user, individual_serial_user
from bson import ObjectId
from fastapi.responses import JSONResponse
from pymongo.collection import ReturnDocument
from typing import Annotated
from auth import get_password_hash
from pymongo.errors import DuplicateKeyError
'''
USER FUNCTIONS
CREATE user
READ user
READ all users 
UPDATE user
DELETE user
'''

router = APIRouter(
    prefix='/users',
    tags=['Users'],
)

@router.post("/", 
        summary="Create a user",
        response_model_by_alias=False,
        status_code=status.HTTP_201_CREATED
    )
async def create_user(user: UserIn):
    existing_user = user_collection.find_one({"username": user.user_display_name})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # Hash the password before storing
    hashed_password = get_password_hash(user.user_password)

    user_in_db = UserInDB(**user.model_dump(by_alias=True, exclude=["id"]),
                          hashed_password=hashed_password,
                          user_reputation=0,
                          user_post_count=0,
                          user_comment_count=0,
                          user_join_date=datetime.now(pytz.timezone('EST')).strftime("%Y-%m-%d %H:%M"),
                          user_role="user"
                          )

    user_result = user_collection.insert_one(user_in_db.model_dump(by_alias=True, exclude=["id"]))

    if user_result.acknowledged:
        created_user = user_collection.find_one({"_id": user_result.inserted_id})
        created_user["_id"] = str(created_user["_id"])

        created_user["user_join_date"] = str(created_user["user_join_date"]) + " EST"
        created_user.pop("hashed_password", None)
        
        # return JSONResponse(content={"message": f"User {created_user['_id']} created"})
        return JSONResponse(content={"message": f"User {created_user['_id']} created",  "user_data": created_user})
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User not created")

@router.get("/",
        summary="Get all users",
        response_model_by_alias=False,
        )
async def get_all_users():
    users = list_serial_user(user_collection.find())
    if users:   
        return users
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No users found.")

@router.get("/{user_id}",
        summary="Get a user",
        response_model_by_alias=False,
        )
async def get_user(user_id: str = Path(description="The ID of the user you'd like to view")):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id format. It must be a valid ObjectId.")
       
    # Use find_one to retrieve the user by ObjectId
    user = user_collection.find_one({"_id": ObjectId(user_id)})
    
    if user:
        # user_out = UserOut(**user).dict()
        user_out = individual_serial_user(user)
        # user_out["user_join_date"] = str(user_out["user_join_date"])
        return JSONResponse(content={user_id : user_out}, status_code=status.HTTP_200_OK)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found.")

@router.put("/{user_id}",
        summary="Update a user",
        response_model_by_alias=False,
        )
async def update_user(user_id: str, user_data: UserUpdate = Body(..., description="The user data to update")):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id format. It must be a valid ObjectId.")
    
    user_data = {k: v for k, v in user_data.model_dump(by_alias=True).items() if v}

    if len(user_data) >= 1:
        update_result = user_collection.find_one_and_update({"_id": ObjectId(user_id)}, 
                                                            {"$set": user_data},
                                                            return_document=ReturnDocument.AFTER,
                                                            )

        if update_result:
            update_result["_id"] = str(update_result["_id"])
            # return update_result
            return JSONResponse(content=update_result, status_code=status.HTTP_200_OK)
        
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")

    # The update is empty, but we should still return the matching document:
    existing_user = user_collection.find_one({"_id": ObjectId(user_id)})
    if existing_user:
        existing_user["_id"] = str(existing_user["_id"])
        return existing_user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")

@router.delete("/{user_id}",
        summary="Delete a user",
        response_model_by_alias=False,
        status_code=status.HTTP_204_NO_CONTENT
        )
async def delete_user(user_id: str = Path(description="The ObjectID of the user you'd like to remove")):

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id format. It must be a valid ObjectId.")

    result = user_collection.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 1:
        return JSONResponse(content={"message": f"User {user_id} removed."}, status_code=status.HTTP_200_OK)
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found.")