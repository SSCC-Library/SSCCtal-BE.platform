from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.rentals import Rental
from models.items import Item
from schemas.return_schema import ReturnRequest, ReturnResponse

router = APIRouter()

@router.post("/api/v0/return", response_model=ReturnResponse)
def return_item(request: ReturnRequest, db: Session = Depends(get_db)):
    rental = db.query(Rental).filter(
        Rental.student_id == request.student_id,
        Rental.item_id == request.item_id,
        Rental.returned == False
    ).first()

    if not rental:
        return ReturnResponse(
            success=False,
            code=404
        )
    
    rental.returned = True
    rental.return_date = request.return_date

    overdue_days = (request.return_date.date() - rental.expectation_return_date).days
    rental.overdue = overdue_days if overdue_days > 0 else 0

    item = db.query(Item).filter(Item.id == request.item_id).first()
    if item:
        item.is_available = "available"

    db.commit()

    return ReturnResponse(
        success=True,
        code=200,
        rental_date= rental.rental_date,
        overdue=rental.overdue
    )