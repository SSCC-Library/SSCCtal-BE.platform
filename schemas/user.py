from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from models.user import UserClassificationEnum,UserStatusEnum,GenderEnum


class UserBase(BaseModel):
    student_id: int
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    gender: Optional[GenderEnum] = GenderEnum.MALE
    major: Optional[str] = None
    major2: Optional[str] = None
    minor: Optional[str] = None
    user_classification: Optional[UserClassificationEnum] = UserClassificationEnum.STUDENT
    user_status: Optional[UserStatusEnum] = UserStatusEnum.ENROLLED

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    update_date: datetime

    model_config = {
        "from_attributes": True
    }

class User(UserBase):
    join_date: datetime
    update_date: datetime

    model_config = {
        "from_attributes": True
    }