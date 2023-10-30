from typing import Optional, List
import uuid
from pydantic import BaseModel

class User(BaseModel):
    user_display_name: Optional[str] = None
    user_email: Optional[str] = None
    user_location: Optional[str] = None
    # user_id: uuid
    # user_name: str
    # user_password: str
    # user_post_count: int
    # user_reputation: int
    # user_join_date: str
    # user_role: str
    
class Comment(BaseModel):
    user_id: str
    post_id: str
    comment_body: Optional[str] = None
    # comment_id: str
    # comment_author: User
    # comment_votes: int
    # comment_timestamp: str

class Post(BaseModel):
    post_title: Optional[str] = None
    post_description: Optional[str] = None
    post_retailer: Optional[str] = None
    # post_id: uuid
    post_comments: Optional[List[Comment]] = None
#     post_author: User
#     post_timestamp: str
#     post_product_category: str
#     post_link_to_deal: str
#     post_views: int
#     post_votes: int
#     post_deal_type: str
#     post_deal_code: str
#     post_deal_expiry: str

