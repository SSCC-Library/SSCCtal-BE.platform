from pydantic import BaseModel
from datetime import datetime, date

class RentalRequest(BaseModel):
    student_id: int
    item_id: int
    rental_date: datetime
    expectation_return_date: date

class RentalResponse(BaseModel):
    success: bool
    code: int
