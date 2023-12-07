import datetime
from typing import Optional, List
import uuid
from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field
from typing_extensions import Annotated
from datetime import datetime
from pytz import timezone

PyObjectId = Annotated[str, BeforeValidator(str)]
tz = timezone('EST')

'''
create a user:
user_full_name
user_display_name
user_password
user_email
user_location
'''
class UserBase(BaseModel):
    user_display_name: str
    user_email: EmailStr | None = None
    user_full_name: str | None = None
    user_location: str | None = None
    

class UserIn(UserBase):
    user_password: str
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "user_display_name": "jane_doe",
                "user_email": "jdoe@gmail.com",
                "user_full_name": "Jane Doe",
                "user_location": "Toronto",
                "user_password": "123456"
            }
        }
    )

class UserUpdate(UserBase):
    user_display_name: str | None = None
    user_password: str | None = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "user_display_name": "jane_doe",
                "user_email": "jdoe@gmail.com",
                "user_full_name": "Jane Doe",
                "user_location": "Toronto",
                "user_password": "123456"
            }
        }
    )

class UserInDB(UserBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    hashed_password: str
    user_reputation: int = 0
    user_post_count: int = 0
    user_comment_count: int = 0
    user_join_date: str = None
    user_role: str = "user"

class UserOut(UserBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_reputation: int
    user_post_count: int 
    user_comment_count: int 
    user_join_date: str 
    user_role: str


class Comment(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    post_id: str
    comment_body: str
    comment_votes: int = 0
    comment_timestamp: datetime = datetime.now(timezone('EST'))
    
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
    # comment_id: str
    # comment_author: User
    # comment_votes: int
    # comment_timestamp: str

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

class Post(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    post_title: str
    post_description: str
    post_retailer: str
    post_votes: int = 0
    post_timestamp: datetime = None
    # post_id: uuid
    # post_comments: Optional[List[Comment]] = None
#     post_author: User
#     post_product_category: str
#     post_link_to_deal: str
#     post_views: int
#     post_votes: int
#     post_deal_type: str
#     post_deal_code: str
#     post_deal_expiry: str
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

class UpdatePost(BaseModel):
    post_title: Optional[str] = None
    post_description: Optional[str] = None
    post_retailer: Optional[str] = None
    # post_id: uuid
    # post_comments: Optional[List[Comment]] = None
#     post_author: User
#     post_timestamp: str
#     post_product_category: str
#     post_link_to_deal: str
#     post_views: int
#     post_votes: int
#     post_deal_type: str
#     post_deal_code: str
#     post_deal_expiry: str
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

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
