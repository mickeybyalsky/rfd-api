from typing import Optional, List
from pydantic import BaseModel, BeforeValidator
from typing_extensions import Annotated

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