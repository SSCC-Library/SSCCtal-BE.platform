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
    join_date: datetime
    update_date: datetime
    user_status: UserStatusEnum
    delete_status: DeletionStatusEnum

    model_config = {
        "from_attributes": True  #딕셔너리 아닌 객체 속성 읽기 허용
    }

class UserMainInfo(BaseModel) :
    student_id: int
    name: str
    email: str
    phone_number: Optional[str]
    gender: GenderEnum
    major: Optional[str]
    major2: Optional[str]
    minor: Optional[str]
    user_classification: Optional[UserClassificationEnum]=UserClassificationEnum.STUDENT

class UserSimpleInfo(BaseModel) :
    student_id: int
    name: str