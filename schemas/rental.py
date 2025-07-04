from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from dependencies import DeletionStatusEnum
from models.rental import RentalStatusEnum

class RentalBase(BaseModel):
    student_id: int
    copy_id: int
    copy_status: Optional[RentalStatusEnum] = RentalStatusEnum.BORROWED
    #rental_classification: Optional[str]
    item_borrow_date: Optional[datetime]
    expectation_return_date: Optional[date]
    item_return_date: Optional[datetime]
    overdue: Optional[int] = 0


class RentalCreate(BaseModel):
    student_id: int
    copy_id: int


class Rental(RentalBase):
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class RentalUpdate(RentalBase):
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }