from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime, date
from models.rental import RentalStatusEnum

class RentalBase(BaseModel):
    student_id: int
    copy_id: int
    rental_status: Optional[RentalStatusEnum] = RentalStatusEnum.BORROWED
    item_borrow_date: Optional[datetime]
    expectation_return_date: Optional[date]
    item_return_date: Optional[datetime]
    overdue: Optional[int] = 0


class RentalCreate(BaseModel):
    student_id: int
    copy_id: int


class Rental(RentalBase):
    create_date: datetime
    update_date: datetime

    model_config = {
        "from_attributes": True
    }

class RentalUpdate(RentalBase):
    update_date: datetime

    model_config = {
        "from_attributes": True
    }



class RentalItemResponse(BaseModel):
    name: str
    status: str
    item_borrow_date: Optional[str]
    expectation_return_date: Optional[str]
    item_return_date: Optional[str]
    overdue: int

    model_config = {
        "from_attributes": True,
        "exclude_none": True
    }

class RentalListResponse(BaseModel):
    success: bool
    code: int
    items: Optional[List[RentalItemResponse]] = None

    model_config = {
        "exclude_none": True
    }