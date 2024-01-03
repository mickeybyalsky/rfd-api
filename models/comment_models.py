import datetime
from typing import Optional, List
import uuid
from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field
from typing_extensions import Annotated
from datetime import datetime
from pytz import timezone

PyObjectId = Annotated[str, BeforeValidator(str)]

class CommentBase(BaseModel):
    comment_body: str

class CommentInDB(CommentBase):
    # id: Optional[PyObjectId] = Field(alias="_id", default=None)
    comment_post_id: str
    comment_author: str
    comment_votes: int = 0
    comment_timestamp: str = None
    users_who_upvoted: List[str] = []
    users_who_downvoted: List[str] = []
    
    # comment_author: User

    model_config = ConfigDict(
    populate_by_name=True,
    arbitrary_types_allowed=True
    # json_schema_extra={
    #     "example": {
    #         "user_id": "dsaadas",
    #         "user_display_name": "jdoe",
    #         "user_email": "jdoe@example.com",
    #         "user_location": "Toronto"
    #     }
    # }
    )

class UpdateComment(BaseModel):
    comment_body: Optional[str] = None
    

    model_config = ConfigDict(
    populate_by_name=True,
    arbitrary_types_allowed=True
    # json_schema_extra={
    #     "example": {
    #         "user_id": "dsaadas",
    #         "user_display_name": "jdoe",
    #         "user_email": "jdoe@example.com",
    #         "user_location": "Toronto"
    #     }
    # }
    )
