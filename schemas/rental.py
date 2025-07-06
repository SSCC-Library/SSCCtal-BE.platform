from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from models.rental import RentalStatusEnum

class RentalBase(BaseModel):
    student_id: int
    copy_id: int
    rental_status: Optional[RentalStatusEnum] = RentalStatusEnum.BORROWED
    #rental_classification: Optional[str]
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