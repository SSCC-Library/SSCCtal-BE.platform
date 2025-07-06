from fastapi import APIRouter, HTTPException,Depends
from models.item import Item
from database import get_db
from sqlalchemy.orm import Session
from typing import List
from schemas.item import ItemCreate, ItemBase
from dependencies import DeletionStatusEnum

router = APIRouter(prefix="/items", tags=["items"])

#아이템 목록 전체 조회
@router.get("/v1", response_model=List[ItemBase])
def get_items(db: Session = Depends(get_db)):
    items = db.query(Item).filter(Item.delete_status!= DeletionStatusEnum.DELETED).all()
    return items

#아이템 id 조회
@router.get("/{item_id}", response_model=ItemBase)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.item_id == item_id,Item.delete_status!= DeletionStatusEnum.DELETED).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

#아이템 추가(테스트용)
@router.post("/v1/create")
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    item = Item(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# 아이템 수정
@router.post("/v1/{item_id}/update", response_model=ItemBase)
def update_item(item_id: int, data: ItemCreate, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.item_id == item_id, Item.delete_status!= DeletionStatusEnum.DELETED).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item

# 아이템 삭제 (soft delete 고려 안함)
@router.post("/v1/{item_id}/delete")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.delete_status = DeletionStatusEnum.DELETED.value
    db.commit()
    return {"success": True, "message": "Item deleted"}