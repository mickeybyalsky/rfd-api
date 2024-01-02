from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Body, status
from auth import get_current_active_user, get_password_hash
from database import user_collection
from models import CreateUserRequest, User, UserOut, UserUpdate
from schemas import list_serial_user, individual_serial_user
from bson import ObjectId
from fastapi.responses import JSONResponse
from pymongo.collection import ReturnDocument
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
    prefix='/api/v1/users',
    tags=['Users'],
)

@router.post("/register", 
        summary="Register a user",
        response_model_by_alias=False,
        status_code=status.HTTP_201_CREATED,
        tags=['default', 'Users']
    )
async def create_user(user: CreateUserRequest):
    try:
        existing_user = user_collection.find_one({"username": user.username})
        
        if existing_user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                detail="Username already registered")

        new_user = User(**user.dict(),
                            hashed_password = get_password_hash(user.password),
                            user_reputation = 0,
                            user_post_count = 0,
                            user_comment_count = 0,
                            user_join_date = str(datetime.now()),
                            user_role = "user"
                            )

        user_result = user_collection.insert_one(dict(new_user))

        if user_result.acknowledged:
            created_user = user_collection.find_one(
                {"_id": user_result.inserted_id},
                projection={"hashed_password": 0}
            )
            created_user["_id"] = str(created_user["_id"])
            
            # return JSONResponse(content={"message": f"User {created_user['_id']} created"})
            return JSONResponse(content={"message": f"User {created_user['_id']} created", 
                                         "user_data": created_user})
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")   

@router.get("/",
        summary="Read all users",
        response_model_by_alias=False,
        )
async def get_all_users():
    users = list_serial_user(user_collection.find(projection={"hashed_password": 0}))
    if users:   
        return users
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="No users found.")

@router.get("/me",
        summary="Read your user",
        response_model_by_alias=False,
        )
async def get_user(current_user: User = Depends(get_current_active_user)):

    existing_user = user_collection.find_one({"username": current_user.username}, 
                                             projection={"hashed_password": 0}
                                            )
    
    if existing_user["username"] != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to view this user."
                            )
    
    if existing_user is not None:
        user = UserOut(**existing_user)
        return JSONResponse(content={current_user.username : dict(user)}, 
                            status_code=status.HTTP_200_OK)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"User '{current_user.username}' not found.")

@router.get("/{username}",
        summary="Read a user",
        response_model_by_alias=False,
        )
async def get_user(username: str = Path(description="The username of the user you want to view")):
    user_in_db = user_collection.find_one({"username": username}, 
                                          projection={"hashed_password": 0})
   
    if user_in_db is not None:
        user = UserOut(**user_in_db)
        return JSONResponse(content={username : dict(user)}, 
                            status_code=status.HTTP_200_OK)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail=f"User '{username}' not found.")

@router.put("/{username}",
        summary="Update a user",
        response_model_by_alias=False,
        )
async def update_user(username: str = Path(..., description="The username of the user you want to update"),
                      user_data: UserUpdate = Body(..., description="The user data to update"),
                      current_user: User = Depends(get_current_active_user)):

    existing_user = user_collection.find_one({"username": username})
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"User {username} not found.") 
    
    if existing_user["post_author"] != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not authorized to update this user.")
    
    update_data = {k: v for k, v in user_data.model_dump(by_alias=True).items() if v}
       
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="No valid fields to update.")
    
    if  len(user_data) >= 1:
        update_result = user_collection.find_one_and_update({"username": username}, 
                                                            {"$set": update_data},
                                                            return_document=ReturnDocument.AFTER,
                                                            )

        if update_result:
            update_result["_id"] = str(update_result["_id"])
            update_result = UserOut(**update_result)
            return JSONResponse(content={username: dict(update_result)}, 
                                status_code=status.HTTP_200_OK)
        
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"User {username} not found")

    # existing_user = user_collection.find_one({"username": ObjectId(username)})
    # if existing_user:
    #     existing_user["_id"] = str(existing_user["_id"])
    #     return existing_user

    # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {username} not found")

@router.delete("/{username}",
        summary="Delete a user",
        response_model_by_alias=False,
        status_code=status.HTTP_204_NO_CONTENT
        )
async def delete_user(username: str = Path(description="The username of the user you want to remove"),
                      current_user: User = Depends(get_current_active_user)):
    
    existing_user = user_collection.find_one({"username": username})
    
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"User {username} not found.")
    
    if existing_user["username"] != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You are not authorized to delete this user.")
    
    result = user_collection.delete_one({"username": username})

    if result.deleted_count == 1:
        return JSONResponse(content={"message": f"User {username} removed."}, 
                            status_code=status.HTTP_200_OK)
    