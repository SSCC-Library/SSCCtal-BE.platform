from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from models.user import UserClassificationEnum,UserStatusEnum
from dependencies import DeletionStatusEnum

class UserBase(BaseModel):
    student_id: int
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    gender: Optional[str] = None
    major: Optional[str] = None
    major2: Optional[str] = None
    minor: Optional[str] = None
    user_classification: Optional[UserClassificationEnum] = UserClassificationEnum.STUDENT
    user_status: Optional[UserStatusEnum] = UserStatusEnum.ENROLLED

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class User(UserBase):
    joined_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }