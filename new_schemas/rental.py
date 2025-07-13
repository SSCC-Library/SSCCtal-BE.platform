from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime, date
from models.rental import RentalStatusEnum
from dependencies import DeletionStatusEnum

class RentalBase(BaseModel):
    rental_id: int
    student_id: int
    copy_id: int
    rental_status: RentalStatusEnum
    item_borrow_date: datetime
    expectation_return_date: date
    item_return_date: Optional[datetime]
    overdue: int
    create_date: datetime
    update_date: datetime
    delete_status: DeletionStatusEnum

class RentalMainInfo(BaseModel) :
    rental_id: int
    student_id: int
    rental_status: RentalStatusEnum
    item_borrow_date: datetime
    expectation_return_date: date
    item_return_date: Optional[datetime]
    overdue: int