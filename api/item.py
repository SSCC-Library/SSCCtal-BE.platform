from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.item import ItemRead
from crud import item as crud_item

router = APIRouter()

@router.get("/items/", response_model=list[ItemRead])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = crud_item.get_items(db, skip=skip,limit=limit)
    return items