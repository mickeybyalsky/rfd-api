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

class PostBase(BaseModel):
    # post_retailer: str
    post_title: str
    post_description: str | None
    post_product_category: str | None
    post_link_to_deal: str | None
    post_deal_expiry: str | None
    post_sale_price: str | None
    post_product_discount: str | None

from pydantic import Field

class PostIn(PostBase):
    post_title: str = Field(
        example="FREE 6 Piece Chicken McNuggets With $1+ Purchase In App",
        description="The title of the post."
    )
    post_description: str = Field(
        example="Free nuggets in the app with $1+ purchase. Labelled as Delivery only but also works for pickup!",
        description="The description of the post."
    )
    post_product_category: str = Field(
        example="Fast Food",
        description="The category of the product."
    )
    post_link_to_deal: str = Field(
        example="In the McD's mobile app!",
        description="The link to the deal."
    ) 
    post_deal_expiry: str = Field(
        example="Dec 7, 2023",
        description="The expiry date of the deal."
    )
    post_sale_price: str = Field(
        example="$1",
        description="The sale price of the product."
    )
    post_product_discount: str = Field(
        example="75%",
        description="The discount percentage of the product."
    )

class PostOut(PostBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    post_votes: int = 0
    post_timestamp: str
    post_author: str
    post_views: int

class PostInDB(PostBase):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    post_votes: int = 0
    post_timestamp: str
    post_author: str
    post_views: int = 0
    post_comments_count: int = 0
    users_who_upvoted: List[str] = []
    users_who_downvoted: List[str] = []

class PostUpdate(PostBase):
    post_title: Optional[str] = Field(
        default=None,
        example="FREE 6 Piece Chicken McNuggets With $1+ Purchase In App",
        description="The title of the post."
    )
    post_description: Optional[str] = Field(
        default=None,
        example="Free nuggets in the app with $1+ purchase. Labelled as Delivery only but also works for pickup!",
        description="The description of the post."
    )
    post_product_category: Optional[str] = Field(
        default=None,
        example="Fast Food",
        description="The category of the product."
    )
    post_link_to_deal: Optional[str] = Field(
        default=None,
        example="In the McD's mobile app!",
        description="The link to the deal."
    ) 
    post_deal_expiry: Optional[str] = Field(
        default=None,
        example="Dec 7, 2023",
        description="The expiry date of the deal."
    )
    post_sale_price: Optional[str] = Field(
        default=None,
        example="$1",
        description="The sale price of the product."
    )
    post_product_discount: Optional[str] = Field(
        default=None,
        example="75%",
        description="The discount percentage of the product."
    )

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
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
