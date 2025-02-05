from datetime import datetime
from auth import get_current_active_user
from models import CreateCommentRequest, CommentInDB, UpdateComment, User
from fastapi import APIRouter, Depends, Form, Path, Body, HTTPException, Query, Request, status
from bson import ObjectId
from fastapi.responses import JSONResponse, RedirectResponse
from pymongo.collection import ReturnDocument
from database import db
from fastapi.templating import Jinja2Templates

router = APIRouter(
    tags=['Comments'],
)

templates = Jinja2Templates(directory="./templates")


def id_to_string(comment):
    comment["id"] = str(comment["_id"])
    del comment["_id"]
    return comment


@router.post("/{post_id}/comments_no_auth",
             summary="Create a comment without authentication",
             description="Create a comment for the provided post_id",
             response_model_by_alias=False,
             status_code=status.HTTP_201_CREATED,
             responses={404: {
                 "description": "Post does not exist. Comment must be created for an existing post."}, 400: {"description": "Invalid post_id format. It must be a valid ID."}, 500: {"description": "Comment not created."}}
             )
async def create_comment_no_auth(new_comment: str = Form(...),
                                 post_id: str = Path(
    description="The ID of the post you would like to comment on."),
):
    # Check if it is a valid ID
    if ObjectId.is_valid(post_id):
        # find the post in the database
        post = db["posts"].find_one({"_id": ObjectId(post_id)})

        # if post does not exist
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                # return an exception
                                detail="Post does not exist. Comment must be created for an existing post.")

    # Not a valid ID
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid post_id format. It must be a valid ID.")  # return an exception

    # Cast comment to CommentInDB model
    new_comment = CommentInDB(
        comment_body=new_comment,
        comment_post_id=post_id,
        comment_author="Anonymous",
        comment_votes=0,
        comment_timestamp=str(datetime.now()),
        users_who_upvoted=[],
        users_who_downvoted=[]
    )

    # Insert the comment into the database
    comment_result = db["comments"].insert_one(new_comment.model_dump())

    # If the comment was successfully inserted
    if comment_result.acknowledged:
        created_comment = db["comments"].find_one(
            {"_id": comment_result.inserted_id}
        )

        # Increment the comment count for the post
        db["posts"].update_one({"_id": ObjectId(post_id)},
                               {"$inc": {"post_comment_count": 1}})

        # Convert the ObjectId to a string
        created_comment['_id'] = str(created_comment['_id'])

        # Return the comment
        return RedirectResponse(url=f"/api/v1/posts/{post_id}", status_code=303)

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Comment not created")  # return an exception


@router.post("/{post_id}/comments",
             summary="Create a comment",
             description="Create a comment for the provided post_id",
             response_model_by_alias=False,
             status_code=status.HTTP_201_CREATED,
             responses={403: {"description": "You are banned from creating comments."}, 404: {
                 "description": "Post does not exist. Comment must be created for an existing post."}, 400: {"description": "Invalid post_id format. It must be a valid ID."}, 500: {"description": "Comment not created."}}
             )
async def create_comment(new_comment: CreateCommentRequest,
                         post_id: str = Path(
                             description="The ID of the post you would like to comment on."),
                         current_user: User = Depends(get_current_active_user)
                         ):

    # check if user is banned
    if current_user["user_role"] == "banned":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are banned from creating posts.")  # return an exception

    # Check if it is a valid ID
    if ObjectId.is_valid(post_id):
        # find the post in the database
        post = db["posts"].find_one({"_id": ObjectId(post_id)})

        # if post does not exist
        if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                # return an exception
                                detail="Post does not exist. Comment must be created for an existing post.")

    # Not a valid ID
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid post_id format. It must be a valid ID.")  # return an exception

    # Cast comment to CommentInDB model
    new_comment = CommentInDB(
        comment_body=new_comment.comment_body,
        comment_post_id=post_id,
        comment_author=current_user['username'],
        comment_votes=0,
        comment_timestamp=str(datetime.now()),
        users_who_upvoted=[],
        users_who_downvoted=[]
    )

    # Insert the comment into the database
    comment_result = db["comments"].insert_one(new_comment.model_dump())

    # If the comment was successfully inserted
    if comment_result.acknowledged:
        created_comment = db["comments"].find_one(
            {"_id": comment_result.inserted_id}
        )

        # Increment the comment count for the user and post
        db["users"].update_one({"username": current_user["username"]},
                               {"$inc": {"user_comment_count": 1}})
        db["posts"].update_one({"_id": ObjectId(post_id)},
                               {"$inc": {"post_comment_count": 1}})

        # Convert the ObjectId to a string
        created_comment['_id'] = str(created_comment['_id'])

        # Return the comment
        return JSONResponse(content={"message": f"Comment {created_comment['_id']} created",
                                     "comment_data": created_comment})

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Comment not created")  # return an exception


@router.get("/{post_id}/add_comment", summary="Render comment form")
async def render_comment_form(request: Request, post_id: str):
    post_title = db["posts"].find_one({"_id": ObjectId(post_id)})["post_title"]
    return templates.TemplateResponse("create_comment.html", {"request": request, "post_id": post_id, "post_title": post_title})


@router.get("/comments/{comment_id}",
            summary="Read a comment",
            description="Retrive a comment object by the comment_id.",
            response_model_by_alias=False,
            responses={404: {"description": "Comment not found."}, 400: {
                "description": "Invalid comment_id format. It must be a valid ID."}, 200: {"description": "Comment found."}}
            )
async def get_comment(comment_id: str = Path(description="The ID of the commment you would like to view")):
    # check if it is a valid ID
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid comment_id format. It must be a valid ID")  # return an exception

    # find the comment in the database
    comment = db["comments"].find_one({"_id": ObjectId(comment_id)})

    # if the comment does not exist, raise an exception
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")
    else:
        comment = id_to_string(comment)  # convert the ObjectId to a string
        return JSONResponse(content=comment,
                            status_code=status.HTTP_200_OK)  # return the comment


@router.get("/posts/{post_id}/comments",
            summary="Read comments for a post",
            description="Retrieve comments for a post by the post_id.",
            response_model_by_alias=False,
            responses={404: {"description": "No comments found."}, 400: {
                "description": "Invalid post_id format. It must be a valid ID."}, 200: {"description": "Comments found."}}
            )
async def get_post_comments(post_id: str):
    # check if it is a valid ID
    if not ObjectId.is_valid(post_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid post_id format. It must be a valid ID")  # return an exception
    # find the post in the database
    post = db["posts"].find_one({"_id": ObjectId(post_id)})

    # if the post does not exist, return an exception
    if not post:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="Post not found.")

    # find the comments for the post
    comments = db["comments"].find({"comment_post_id": post_id})
    
    # convert the ObjectId to a string for each comment
    comments = [id_to_string(comment) for comment in comments]
    
    return JSONResponse(content=comments,
                        status_code=status.HTTP_200_OK)  # return the comments


@router.get("/comments",
            summary="Read comments with optional filters",
            description="Retrieve comments with optional filters for username and/or post ID. Leave fields blank to retrive all comments.",
            responses={200: {"description": "Comments found."}, 404: {"description": "No comments found."}, 400: {
                "description": "Invalid post_id format. It must be a valid ID."}}
            )
async def get_comments_filtered(username: str | None = Query(None, description="Optional. The username to filter comments.")):
    filter_params = {}  # create an empty dictionary for the filter parameters

    # if username is provided
    if username:
        # find the user in the database
        user = db["users"].find_one({"username": username})

        # if the user does not exist, raise an exception
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found.")

        # set the username to be a filter parameter
        filter_params["comment_author"] = username

    # if there are comments that match the filter parameters
    if db["comments"].count_documents(filter_params) > 0:
        # find the comments that match the filter parameters
        comments_result = db["comments"].find(filter_params)
        comments_result = [id_to_string(comment)
                           # convert the ObjectId to a string for each comment
                           for comment in comments_result]

        # if the user entered filters
        if filter_params:
            return JSONResponse(content={f"Comments for the query {filter_params} ": comments_result},
                                status_code=status.HTTP_200_OK)

        # if the user did not enter filters return generic message
        else:
            return JSONResponse(content={f"No filters provided. All commnents were returned ": comments_result},
                                status_code=status.HTTP_200_OK)


@router.put("/comments/{comment_id}",
            summary="Update a Comment",
            description="Updates a comment object by the comment_id and provided request body.",
            response_model_by_alias=False,
            responses={404: {"description": "Comment not found."}, 400: {
                "description": "Invalid comment_id format. It must be a valid ID."}, 403: {"description": "You are not authorized to update this comment."}, 200: {"description": "Comment updated."}}
            )
async def update_comment(comment_id: str = Path(description="The ID of the comment you would like to update."),
                         current_user: User = Depends(get_current_active_user),
                         comment_data: UpdateComment = Body(..., description="The comment data to update")):
    # check if it is a valid ID
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid comment_id format. It must be a valid ID.")  # return an exception

    # find the comment in the database
    existing_comment = db["comments"].find_one({"_id": ObjectId(comment_id)})

    # if the comment does not exist, raise an exception
    if not existing_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Comment {comment_id} not found.")

    # if the comment author is not the current user, raise an exception
    if existing_comment["comment_author"] != current_user["username"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to update this comment.")

    # create a dictionary of the fields to update
    comment_data = {k: v for k, v in comment_data.model_dump(
        by_alias=True).items() if v}

    # if there are no valid fields to update, raise an exception
    if not comment_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No valid fields to update.")

    # update the comment in the database if there are valid fields to update
    if len(comment_data) >= 1:
        update_result = db["comments"].find_one_and_update({"_id": ObjectId(comment_id)},
                                                           {"$set": comment_data},
                                                           return_document=ReturnDocument.AFTER,
                                                           )
        # convert the ObjectId to a string
        if update_result:
            update_result["_id"] = str(update_result["_id"])
            return JSONResponse(content=update_result,
                                status_code=status.HTTP_200_OK)  # return the updated comment

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        # return an exception
                        detail=f"Comment {comment_id} not found.")


@router.delete("/comments/{comment_id}",
               summary="Delete a comment",
               response_model_by_alias=False,
               description="Delete a comment object by the comment_id",
               status_code=status.HTTP_204_NO_CONTENT,
               responses={404: {"description": "Comment not found."}, 400: {
                   "description": "Invalid comment_id format. It must be a valid ID."}, 403: {"description": "You are not authorized to delete this comment."}, 200: {"description": "Comment removed."}}
               )
async def delete_comment(comment_id: str = Path(description="The ID of the comment you would like to remove"),
                         current_user: User = Depends(get_current_active_user)):
    # check if it is a valid ID
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid comment_id format. It must be a valid ID.")

    # find the comment in the database
    existing_comment = db["comments"].find_one({"_id": ObjectId(comment_id)})
    post_id = existing_comment["_id"]  # get the post_id

    # if the comment does not exist, raise an exception
    if not existing_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Comment {comment_id} not found.")

    # if the comment author is not the current user, raise an exception
    if existing_comment["comment_author"] != current_user["username"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to delete this comment.")

    # delete the comment from the database
    result = db["comments"].delete_one({"_id": ObjectId(comment_id)})

    # if the comment was successfully deleted
    if result.deleted_count == 1:

        # decrement the comment count for the user
        db["users"].update_one({"username": current_user["username"]},
                               {"$inc": {"user_comment_count": -1}}
                               )

        # decrement the comment count for the [pst]
        db["posts"].update_one({"_id": post_id},
                               {"$inc": {"post_comment_count": -1}})

        # return a success message
        return JSONResponse(content={"message": f"Comment {comment_id} removed."},
                            status_code=status.HTTP_200_OK)

    # if the comment was not found, raise an exception
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Comment {comment_id} not found.")


@router.post("/comments/{comment_id}/upvote",
             summary="Upvote a comment",
             response_model_by_alias=False,
             description="Upvote a comment object based on the comment_id",
             status_code=status.HTTP_200_OK,
             responses={404: {"description": "Comment not found."}, 400: {
                 "description": "Invalid comment_id format. It must be a valid ID."}, 200: {"description": "Comment upvoted."}}
             )
async def upvote_comment(comment_id: str = Path(description="The ID of the commment to upvote"),
                         current_user: User = Depends(get_current_active_user)):

    # check if it is a valid ID
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid comment_id format. It must be a valid ID")

    user = current_user["username"]  # create an alias

    # find the comment in the database
    existing_comment = db["comments"].find_one({"_id": ObjectId(comment_id)})

    # if the comment does not exist, raise an exception
    if not existing_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Comment not found.")

    # cannot vote on own comment, so raise an exception
    if existing_comment["comment_author"] == current_user["username"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot vote on your own comment!")

    # user not in upvoted and not in downvoted -> add 1 to upvote
    if user not in existing_comment["users_who_upvoted"] and user not in existing_comment["users_who_downvoted"]:
        # add 1 to the comment_votes and add the user to the users_who_upvoted array
        result = db["comments"].update_one(
            {"_id": ObjectId(comment_id)},
            {
                "$inc": {"comment_votes": 1},
                "$push": {"users_who_upvoted": user}
            }
        )

        # if the comment was successfully upvoted, return a success message
        if result.modified_count == 1:
            return JSONResponse(content=f"Comment {comment_id} upvoted!",
                                status_code=status.HTTP_200_OK)

    # user in downvoted and not in upvoted -> remove from down, add to up and add 2 (1 to cancel downvote, 1 for upvote)
    if user not in existing_comment["users_who_upvoted"] and user in existing_comment["users_who_downvoted"]:
        # add 2 to the comment_votes, remove the user from the users_who_downvoted array, and add the user to the users_who_upvoted array
        result = db["comments"].update_one(
            {"_id": ObjectId(comment_id)},
            {
                "$inc": {"comment_votes": 2},
                "$pull": {"users_who_downvoted": user},
                "$push": {"users_who_upvoted": user}
            }
        )

        # if the comment was successfully upvoted, return a success message
        if result.modified_count == 1:
            return JSONResponse(content=f"Comment {comment_id} upvoted!",
                                status_code=status.HTTP_200_OK)

    # if user already upvoted the comment, raise an exception
    if user in existing_comment["users_who_upvoted"] and user not in existing_comment["users_who_downvoted"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You already upvoted this comment!")

    # increment the comment_author's reputation
    db["users"].update_one(
        {"username": existing_comment["comment_author"]},
        {"$inc": {"user_reputation": 1}},
    )


@router.post("/comments/{comment_id}/downvote",
             summary="Downvote a comment",
             response_model_by_alias=False,
             description="Downvote a comment object based on the comment_id",
             status_code=status.HTTP_200_OK,
             responses={404: {"description": "Comment not found."}, 400: {
                 "description": "Invalid comment_id format. It must be a valid ID."}, 200: {"description": "Comment upvoted."}}
             )
async def downvote_comment(comment_id: str = Path(description="The ID of the commment to upvote"),
                           current_user: User = Depends(get_current_active_user)):
    # check if it is a valid ID, else raise an exception
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid comment_id format. It must be a valid ID")

    user = current_user["username"]  # create an alias

    # find the comment in the database
    existing_comment = db["comments"].find_one({"_id": ObjectId(comment_id)})

    # if the comment does not exist, raise an exception
    if not existing_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Comment not found.")

    # cannot vote on own post so raise an exception
    if existing_comment["comment_author"] == current_user["username"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Cannot vote on your own post!")

    # user not in upvoted and not in downvoted -> add -1 to votes
    if user not in existing_comment["users_who_upvoted"] and user not in existing_comment["users_who_downvoted"]:

        # add -1 to the comment_votes and add the user to the users_who_downvoted array
        result = db["comments"].update_one(
            {"_id": ObjectId(comment_id)},
            {
                "$inc": {"comment_votes": -1},
                "$push": {"users_who_downvoted": user}
            }
        )

        # if the comment was successfully downvoted, return a success message
        if result.modified_count == 1:
            return JSONResponse(content=f"Comment {comment_id} downvoted",
                                status_code=status.HTTP_200_OK)

    # user in upvoted and not in downvoted -> remove from up, add to downvoted and add -2 (1 to downvote, 1 to cancel upvote)
    if user not in existing_comment["users_who_downvoted"] and user in existing_comment["users_who_upvoted"]:

        # add -2 to the comment_votes, remove the user from the users_who_upvoted array, and add the user to the users_who_downvoted array
        result = db["comments"].update_one(
            {"_id": ObjectId(comment_id)},
            {
                "$inc": {"comment_votes": -2},
                "$pull": {"users_who_upvoted": user},
                "$push": {"users_who_downvoted": user}
            }
        )

        # if the comment was successfully downvoted, return a success message
        if result.modified_count == 1:
            return JSONResponse(content=f"Comment {comment_id} downvoted.",
                                status_code=status.HTTP_200_OK)

    # if user already downvoted the comment, raise an exception
    if user in existing_comment["users_who_downvoted"] and user not in existing_comment["users_who_upvoted"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You already downvoted this comment!")

    # decrement the comment_author's reputation
    db["users"].update_one(
        {"username": existing_comment["comment_author"]},
        {"$inc": {"user_reputation": -1}},
    )


@router.post("/comments/{comment_id}/upvote_no_auth",
             summary="Upvote a comment without auth",
             response_model_by_alias=False,
             description="Upvote a comment object based on the comment_id without auth",
             status_code=status.HTTP_200_OK,
             responses={404: {"description": "Comment not found."}, 400: {
                 "description": "Invalid comment_id format. It must be a valid ID."}, 200: {"description": "Comment upvoted."}}
             )
async def upvote_comment_no_auth(comment_id: str = Path(description="The ID of the commment to upvote")):

    # check if it is a valid ID
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid comment_id format. It must be a valid ID")

    # find the comment in the database
    existing_comment = db["comments"].find_one({"_id": ObjectId(comment_id)})

    # if the comment does not exist, raise an exception
    if not existing_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Comment not found.")
   
    result = db["comments"].update_one(
        {"_id": ObjectId(comment_id)},
        {
            "$inc": {"comment_votes": 1}
        }
    )
    # increment the comment_author's reputation
    db["users"].update_one(
        {"username": existing_comment["comment_author"]},
        {"$inc": {"user_reputation": 1}},
    )

    # if the comment was successfully upvoted, return a success message
    if result.modified_count == 1:
        return JSONResponse(content={"message": f"Comment upvoted."},
                            status_code=status.HTTP_200_OK)
    
@router.post("/comments/{comment_id}/downvote_no_auth",
             summary="Downvote a comment without auth",
             response_model_by_alias=False,
             description="Downvote a comment object based on the comment_id without auth",
             status_code=status.HTTP_200_OK,
             responses={404: {"description": "Comment not found."}, 400: {
                 "description": "Invalid comment_id format. It must be a valid ID."}, 200: {"description": "Comment upvoted."}}
             )
async def downvote_comment_no_auth(comment_id: str = Path(description="The ID of the commment to upvote")):
    # check if it is a valid ID
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid comment_id format. It must be a valid ID")

    # find the comment in the database
    existing_comment = db["comments"].find_one({"_id": ObjectId(comment_id)})

    # if the comment does not exist, raise an exception
    if not existing_comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Comment not found.")
   
    result = db["comments"].update_one(
        {"_id": ObjectId(comment_id)},
        {
            "$inc": {"comment_votes": -1}
        }
    )
    # increment the comment_author's reputation
    db["users"].update_one(
        {"username": existing_comment["comment_author"]},
        {"$inc": {"user_reputation": -1}},
    )

    # if the comment was successfully upvoted, return a success message
    if result.modified_count == 1:
        return JSONResponse(content={"message": f"Comment downvoted."},
                            status_code=status.HTTP_200_OK)
