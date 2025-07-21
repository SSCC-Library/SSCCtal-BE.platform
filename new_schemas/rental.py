from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime, date
from models.rental import RentalStatusEnum
from dependencies import DeletionStatusEnum
from models.item import ItemTypeEnum

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

class OverdueResponse(BaseModel):
    rental_id: int
    name: Optional[str] = None        # 책 제목
    type: Optional[ItemTypeEnum] = None        # 책 / 기자재 등
    user_name: Optional[str] = None
    student_id: Optional[str] = None
    item_borrow_date: Optional[datetime] = None
    item_return_date: Optional[datetime] = None
    rental_status: Optional[RentalStatusEnum] = None
    overdue: int
    model_config = {
        "from_attributes": True,
        "use_enum_values": True
    }

class RentalStatusUpdate(BaseModel) :
    rental_status : RentalStatusEnum