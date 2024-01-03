from pydantic import BaseModel, ConfigDict
import datetime
from typing import Optional, List
import uuid
from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field
from typing_extensions import Annotated
from datetime import datetime
from pytz import timezone


class CreateUserRequest(BaseModel):
    username: str
    password: str
    user_email: str | None = None
    user_full_name: str | None = None
    user_location: str | None = None

class User(BaseModel):
    username: str
    hashed_password: str
    user_email: str | None = None
    user_full_name: str | None = None
    user_location: str | None = None
    user_reputation: int = 0
    user_post_count: int = 0
    user_comment_count: int = 0
    user_join_date: str = None
    user_role: str = "user"

class UserUpdate(BaseModel):
    user_email: str | None = None
    user_full_name: str | None = None
    user_location: str | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "user_email": "this_is_a_password",
                "user_full_name": "Jane Doe",
                "user_location": "Toronto",
            }
        }
    )

# class UserInDB(BaseModel):
#     # id: Optional[PyObjectId] = Field(alias="_id", default=None)
#     user_reputation: int = 0
#     user_post_count: int = 0
#     user_comment_count: int = 0
#     user_join_date: str = None
#     user_role: str = "user"

class UserOut(BaseModel):
    username: str
    user_email: str | None = None
    user_full_name: str | None = None
    user_location: str | None = None
    user_reputation: int = 0
    user_post_count: int = 0
    user_comment_count: int = 0
    user_join_date: str = None
    user_role: str = "user"
    