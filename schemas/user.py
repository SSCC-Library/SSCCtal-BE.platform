from pydantic import BaseModel, EmailStr
from typing import Optional,List
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
    join_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    user_classification: Optional[UserClassificationEnum] = UserClassificationEnum.STUDENT
    user_status: Optional[UserStatusEnum] = UserStatusEnum.ENROLLED

    model_config = {
        "from_attributes": True 
    }

class UsersBase(BaseModel) :
    student_id: int
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    gender: Optional[GenderEnum] = GenderEnum.MALE
    major: Optional[str] = None
    major2: Optional[str] = None
    minor: Optional[str] = None

class UserCreate(BaseModel):
    student_id: int
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    gender: Optional[GenderEnum] = GenderEnum.MALE
    major: Optional[str] = None
    major2: Optional[str] = None
    minor: Optional[str] = None
    user_classification: Optional[UserClassificationEnum] = UserClassificationEnum.STUDENT

class UserUpdate(BaseModel):
    student_id: int
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    major: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class UserResponse(BaseModel):
    success : bool
    code : int
    user : Optional[UserBase]=None

    model_config = {
        "from_attributes": True
    }

class UsersResponse(BaseModel) :
    success : bool
    code : int
    user : Optional[UsersBase]=None

    model_config = {
        "from_attributes": True
    }

class PersonalRentalItem(BaseModel):
    name: str
    status: str
    item_borrow_date: str
    expectation_return_date: str
    item_return_date: Optional[str]
    overdue: Optional[int]=None

class PersonalRentalListResponse(BaseModel):
    success: bool
    code: int
    items: Optional[List[PersonalRentalItem]]=None
    page: Optional[int]=None
    size: Optional[int]=None

    model_config = {
        "from_attributes": True
    }