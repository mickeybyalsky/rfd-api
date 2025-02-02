import datetime
from typing import Optional, List
import uuid
from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field
from typing_extensions import Annotated
from datetime import datetime
# from pytz import timezone

PyObjectId = Annotated[str, BeforeValidator(str)]

class CreateCommentRequest(BaseModel):
    comment_body: str

class CommentInDB(BaseModel):
    # id: Optional[PyObjectId] = Field(alias="_id", default=None)
    comment_body: str
    comment_post_id: str
    comment_author: str
    comment_votes: int = 0
    comment_timestamp: str = None
    users_who_upvoted: List[str] = []
    users_who_downvoted: List[str] = []

class UpdateComment(BaseModel):
    comment_body: Optional[str] = None