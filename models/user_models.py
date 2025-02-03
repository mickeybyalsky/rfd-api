from pydantic import BaseModel
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, description="Unique username")
    password: str = Field(..., min_length=6, max_length=100, description="User password")
    user_email: EmailStr  # Using Pydantic EmailStr for validation
    user_full_name: Optional[str] = None
    user_location: Optional[str] = None

class User(BaseModel):
    username: str
    hashed_password: str
    user_email: Optional[EmailStr] = None
    user_full_name: Optional[str] = None
    user_location: Optional[str] = None
    user_reputation: int = 0
    user_post_count: int = 0
    user_comment_count: int = 0
    user_join_date: str | None = None
    user_role: str = "user"
    user_spent_total: int = 0
    users_purchases: List[str] = []

class UserUpdate(BaseModel):
    user_email: Optional[EmailStr] = None
    user_full_name: Optional[str] = None
    user_location: Optional[str] = None

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
    