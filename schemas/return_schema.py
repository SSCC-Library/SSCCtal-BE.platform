from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReturnRequest(BaseModel):
    student_id: int
    item_id: int
    return_date: datetime

class ReturnResponse(BaseModel):
    success: bool
    code: int
    rental_date: Optional[datetime] = None
    overdue: Optional[int] = None
