from pydantic import BaseModel, EmailStr
from typing import Optional,List
from datetime import datetime
from models.user import UserClassificationEnum,UserStatusEnum,GenderEnum
from dependencies import DeletionStatusEnum

class UserBase(BaseModel):
    id: int
    student_id: int
    name: str
    email: str
    phone_number: Optional[str]
    gender: GenderEnum
    major: Optional[str]
    major2: Optional[str]
    minor: Optional[str]
    user_classification: UserClassificationEnum
    joined_at: datetime
    updated_at: datetime
    user_status: UserStatusEnum
    delete_status: DeletionStatusEnum

class UserMainInfo(BaseModel) :
    student_id: int
    name: str
    email: str
    phone_number: Optional[str]
    gender: GenderEnum
    major: Optional[str]
    major2: Optional[str]
    minor: Optional[str]

