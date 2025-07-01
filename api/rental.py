from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.rental import RentalRead
from crud import rental as crud_rental

router = APIRouter()

@router.get("/rentals/", response_model=list[RentalRead])
def read_rentals(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    rentals = crud_rental.get_rentals(db, skip=skip, limit=limit)
    return rentals
