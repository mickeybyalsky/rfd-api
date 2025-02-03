from typing import Optional, List
from pydantic import BaseModel, BeforeValidator
from typing_extensions import Annotated
from typing import List
PyObjectId = Annotated[str, BeforeValidator(str)]

# class PostBase(BaseModel):
#     # post_retailer: str
#     post_title: str
#     post_description: str | None
#     post_product_category: str | None
#     post_link_to_deal: str | None
#     post_deal_expiry: str | None
#     post_sale_price: str | None
#     post_product_discount: str | None

class CreatePostRequest(BaseModel):
    post_title: str 
    post_description: str 
    post_product_category:  Optional[str] = None
    post_link_to_deal:  Optional[str] = None 
    post_deal_expiry:  Optional[str] = None 
    post_sale_price:  Optional[int] = None 
    post_retailer:  Optional[str] = None

class PostInDB(BaseModel):
    post_title: str 
    post_description: str 
    post_product_category:  Optional[str] = None
    post_link_to_deal:  Optional[str] = None 
    post_deal_expiry:  Optional[str] = None 
    post_sale_price:  Optional[int] = None 
    post_retailer:  Optional[str] = None
    post_votes: int = 0  # Initial vote count
    post_timestamp: str| None = None
    post_author: str  # Username of the post creator
    post_views: int = 0  # Track how many people viewed the post
    post_comments_count: int = 0  # Number of comments
    users_who_upvoted: List[str] = []  # Track upvoters
    users_who_downvoted: List[str] = []  # Track downvoters
    bought_count: int = 0  # Track how many people bought the product
    

class PostUpdate(BaseModel):
    post_title: Optional[str] = None
    post_description: Optional[str] = None
    post_product_category: Optional[str] = None
    post_link_to_deal: Optional[str] = None
    post_deal_expiry: Optional[str] = None
    post_sale_price: Optional[int] = None
    post_product_discount: Optional[str] = None
