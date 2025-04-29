from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.rental import RentalRequest, RentalResponse
from models.rentals import Rental
from models.items import Item

router = APIRouter()

@router.post("/api/v0/rental", response_model=RentalResponse)
def rental_item(request: RentalRequest, db: Session = Depends(get_db)):
    rental = Rental(
        student_id=request.student_id,
        item_id=request.item_id,
        rental_date=request.rental_date,
        expectation_return_date=request.expectation_return_date,
        returned=False,
        overdue=0
    )
    db.add(rental)
    
    item = db.query(Item).filter(Item.id == request.item_id).first()

    if not item:
        return RentalResponse(
            success=False,
            code=404
        )
    
    item.is_available = "rented"

    db.commit()

    return RentalResponse(
        success=True,
        code=200
    )