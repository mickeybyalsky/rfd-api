from typing import Optional, List
import uuid
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_display_name: str
    user_email: str
    user_location: Optional[str] = None

    model_config = ConfigDict(
    populate_by_name=True,
    arbitrary_types_allowed=True,
    json_schema_extra={
        "example": {
            "name": "Jane Doe",
            "user_display_name": "jdoe",
            "user_email": "jdoe@example.com",
            "user_location": "Toronto"
        }
    })

    # user_id: uuid
    # user_name: str
    # user_password: str
    # user_post_count: int
    # user_reputation: int
    # user_join_date: str
    # user_role: str

class UpdateUser(BaseModel):
    user_display_name: Optional[str] = None
    user_email: Optional[str] = None
    user_location: Optional[str] = None

    model_config = ConfigDict(
    populate_by_name=True,
    arbitrary_types_allowed=True,
    json_schema_extra={
        "example": {
            "name": "Jane Doe",
            "user_display_name": "jdoe",
            "user_email": "jdoe@example.com",
            "user_location": "Toronto"
        }
    })
    
class Comment(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    post_id: str
    comment_body: str
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