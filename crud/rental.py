from sqlalchemy.orm import Session
from models.rental import Rental

def get_rentals(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Rental).offset(skip).limit(limit).all()
