from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.items import Item
from schemas.item import ManualInputRequest, ItemResponse

router = APIRouter()

@router.post("/api/v0/manual/input", response_model=ItemResponse)
def manual_input(request: ManualInputRequest, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.isbn == request.isbn).first()

    if not db_item:
        return ItemResponse(
            success=False,
            code=404
        )

    return ItemResponse(
        success=True,
        code=200,
        item_id=db_item.id,
        title=db_item.name,
        status=db_item.is_available,
        img=db_item.img
    )