from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Path, Body, Request, status
from fastapi.templating import Jinja2Templates
from auth import get_current_active_user, get_password_hash
from models.user_models import CreateUserRequest, User, UserOut, UserUpdate
from bson import ObjectId
from fastapi.responses import JSONResponse
from pymongo.collection import ReturnDocument
from database import db

router = APIRouter(
    prefix='/users',
    tags=['Users'],
)

templates = Jinja2Templates(directory="./templates")

def id_to_string(user):
    user["id"] = str(user["_id"])
    del user["_id"]
    return user

@router.post("/register",
             summary="Register a user",
             response_model_by_alias=False,
             status_code=status.HTTP_201_CREATED,
             tags=['default', 'Users'],
             description="Create a new user.",
             responses={400: {"description": "Username already exists."}}
             )
async def create_user(user: CreateUserRequest):
    # Check if username already exists
    existing_user = db["users"].find_one({"username": user.username})

    # If user already exists, raise an error
    if existing_user:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username already registered. Please select another username.")

    # Hash password before storing in the database
    hashed_password = get_password_hash(user.password)

    # Cast CreateUserRequest to a dictionary of User
    user_data = User(
        username=user.username,
        hashed_password=hashed_password,
        user_email=user.user_email,
        user_full_name=user.user_full_name,
        user_location=user.user_location,
        user_reputation=0,
        user_post_count=0,
        user_comment_count=0,
        user_join_date=str(datetime.utcnow()),
        user_role="user",
        user_spent_total=0
    ).model_dump()

    # Insert user data into the database
    user_result = db["users"].insert_one(user_data)

    # Get the created user from the database, exclude the hashed password
    created_user = db["users"].find_one(
        {"_id": user_result.inserted_id},
        projection={"hashed_password": 0}
    )

    # Convert ObjectId to string
    created_user["_id"] = str(created_user["_id"])

    # Return the created user
    return JSONResponse(content={"message": f"User {created_user['_id']} created",
                                 "user_data": created_user})


@router.get("/",
            summary="Read all users",
            response_model_by_alias=False,
            description="Retrive all users.",
            responses={404: {"description": "No Users found."}}
            )
async def get_all_users(request: Request):
    # Get all users from the database, do not include the hashed password
    users = list(db["users"].find(projection={"hashed_password": 0}))

    # If users found, return the users
    if users:
        # Convert all ObjectId to string
        output = [id_to_string(user) for user in users]
        return templates.TemplateResponse("users.html", {"request": request, "name": "RedFlagDeals REST API", "users": output})
    else:
        # If no users found, raise an error
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No users found.")


@router.get("/me",
            summary="Read your user",
            response_model_by_alias=False,
            description="Retrive information about the logged in user.",
            responses={403: {"description": "You are not authorized."},
                       404: {"description": "User not found."}}
            )
async def get_current_user(current_user: User = Depends(get_current_active_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")

    # Get the logged in user from the database, exclude the hashed password
    existing_user = db["users"].find_one({"username": current_user["username"]},
                                         projection={"hashed_password": 0})

    # If user exists return data, If user not found, raise an error
    if existing_user:
        user = id_to_string(existing_user)  # Convert ObjectId to string
        return JSONResponse(content={current_user["username"]: dict(user)},
                                status_code=status.HTTP_200_OK)  # Return the updated user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            # raise an error
                            detail=f"User '{current_user["username"]}' not found.")


@router.get("/{username}",
            summary="Read a user",
            response_model_by_alias=False,
            description="Retrive a user by the username",
            responses={404: {"description": "User not found."}}
            )
async def get_user(request: Request, username: str = Path(description="The username of the user you want to view")):
    # Get the user by the username, exclude the hashed password
    user_in_db = db["users"].find_one({"username": username},
                                      projection={"hashed_password": 0})
    # If user not found, raise an error
    if user_in_db:
        user = id_to_string(user_in_db)  # convert ObjectId to string
        return templates.TemplateResponse("user_detail.html", {"request": request, "user": user})
        
    # If user not found, raise an error
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"User '{username}' not found.")


@router.put("/",
            summary="Update a user",
            response_model_by_alias=False,
            description="Updates a user by the username.",
            responses={400: {"description": "No valid fields to update"}, 403: {
                "description": "You are not authorized."}, 404: {"description": "User not found."}}
            )
async def update_user(user_data: UserUpdate = Body(..., description="The user data to update"),
                      current_user: User = Depends(get_current_active_user)):

    # Turn updated data into a dictionary
    update_data = {key: value for key, value in user_data.model_dump(
        by_alias=True).items() if value is not None}

    # If no valid fields to update, raise an error
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No valid fields to update.")

    # If there are fields to update, update the user
    if len(update_data) >= 1:
        update_result = db["users"].find_one_and_update({"username": current_user["username"]},
                                                        {"$set": update_data},
                                                        return_document=ReturnDocument.AFTER,
                                                        )
        # If user not found, raise an error
        if update_result:

            # Convert ObjectId to string
            update_result["_id"] = str(update_result["_id"])
            update_result = UserOut(**update_result)
            return JSONResponse(content={current_user["username"]: dict(update_result)},
                                status_code=status.HTTP_200_OK)  # Return the updated user

        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User {current_user["username"]} not found")


@router.delete("/{username}",
               summary="Delete a user",
               response_model_by_alias=False,
               status_code=status.HTTP_204_NO_CONTENT,
               description="Deletes a user by the username.",
               responses={403: {"description": "You are not authorized."}, 404: {
                   "description": "User not found."}}
               )
async def delete_user(username: str = Path(description="The username of the user you want to remove"),
                      current_user: User = Depends(get_current_active_user)):

    # Get the user by the username
    existing_user = db["users"].find_one({"username": username})

    # If user not found, raise an error
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User {username} not found.")

    # If user is not the current user, raise an error
    if existing_user["username"] != current_user["username"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You are not authorized to delete this user.")

    # If user is the current user, delete the user
    result = db["users"].delete_one({"username": username})

    # If user is deleted, return a message
    if result.deleted_count == 1:
        return JSONResponse(content={"message": f"User {username} removed."},
                            status_code=status.HTTP_200_OK)


@router.post("/purchases/{post_id}/add",
             summary="Add a product to the user's bought list",
             status_code=status.HTTP_201_CREATED,
             description="Add a product to the user's bought list.",
             responses={404: {"description": "Product not found."}, 200: {"description": "Product added to user's bought list."}}
             )
async def bought_product(current_user: User = Depends(get_current_active_user),
                         post_id: str = Path(..., description="The post ID of the product you bought")):
    
    # Check if product exists
    product = db["posts"].find_one({"_id": ObjectId(post_id)})  

    # If product not found, raise an error
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product {post_id} not found.")

    # Increment the bought count of the product by 1
    db["posts"].update_one(
        {"_id": ObjectId(post_id)},
        {
            "$inc": {"bought_count": 1}
        }
    )

    # Increment the user's total spending by the product's price and add the product to the user's bought list
    result = db["users"].update_one(
        {"username": current_user["username"]},
        {
            "$inc": {"user_spent_total": product["post_sale_price"]},
            "$push": {
                "users_purchases": {
                    "deal_id": post_id,
                    "product_title": product["post_title"],
                    "product_price": product["post_sale_price"]
                }
            }
        }
    )

    # If user's purchase is added to profile
    if result.acknowledged:
       
        # Get the current user
        updated_user = db["users"].find_one(
            {"username": current_user["username"]})

        # Get the updated user's total spending
        updated_spent_total = updated_user["user_spent_total"] if updated_user else 0
        # return a message
        return JSONResponse(content={"message": f"Added ${product["post_sale_price"]} to {current_user["username"]}'s spending this year's total. Total spent: ${updated_spent_total}"},
                            status_code=status.HTTP_200_OK)


@router.get("/purchases/total",
            summary="Read the user's bought list",
            description="Retrive the user's bought list.",
            responses={404: {"description": "No products bought."}, 200: {"description": "User's purchases to date."}}
            )
async def get_bought_list(current_user: User = Depends(get_current_active_user)):

    # find the user by the username
    user = db["users"].find_one(
        {"username": current_user["username"]})

    # If user does not exist, raise an error
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No products bought.")
    
    # return the user's bought list and total spending
    return JSONResponse(content={"message": f"{current_user["username"]}'s purchases to date.",
                                 "purchases": user["users_purchases"]},
                        status_code=status.HTTP_200_OK)


@router.post("/purchases/{post_id}/remove",
             summary="Remove a product from the user's bought list",
             status_code=status.HTTP_201_CREATED,
             deprecated=True,
             description="Remove a product from the user's bought list. CURRENTLY ONLY DECEREMENTS THE BOUGHT COUNT OF THE PRODUCT, AND DOES NOT REMOVE ENTRY.",
             )
async def remove_product(current_user: User = Depends(get_current_active_user),
                         post_id: str = Path(..., description="The post ID of the product you bought")):
    product = db["posts"].find_one({"_id": ObjectId(post_id)})
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product {post_id} not found.")

    db["posts"].update_one(
        {"_id": ObjectId(post_id)},
        {
            "$inc": {"bought_count": -1}
        }
    )

    result = db["users"].update_one(
        {"username": current_user["username"]},
        {
            "$inc": {"user_spent_total": -product["post_sale_price"]},
            "$push": {
                "users_purchases": {
                    "deal_id": post_id,
                    "product_title": product["post_title"],
                    "product_price": -product["post_sale_price"]
                }
            }
        }
    )
    if result.acknowledged:
        return JSONResponse(content={"message": f"Removed ${product["post_sale_price"]} from {current_user["username"]}'s spending this year's total."},
                            status_code=status.HTTP_200_OK)
