from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class RentalRead(BaseModel):
    id: int
    student_id: int
    item_id: int
    rental_date: datetime
    expectation_return_date: date
    return_date: Optional[datetime] = None
    overdue: Optional[int] = None
    returned: Optional[bool] = None
    wish_student_id: Optional[int] = None

    class Config:
        orm_mode = True

class RentalRequest(BaseModel):
    student_id: int
    item_id: int
    rental_date: datetime
    expectation_return_date: date

class RentalResponse(BaseModel):
    success: bool
    code: int
