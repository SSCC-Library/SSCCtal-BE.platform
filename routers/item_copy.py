from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from models.item import ItemCopy
from schemas.item import ItemCopyCreate,ItemCopyUpdate, ItemCopySchemas
from database import get_db
from dependencies import DeletionStatusEnum

router = APIRouter(prefix="/copies", tags=["copies"])


# 전체 복사본 조회
@router.get("/", response_model=List[ItemCopySchemas])
def get_copies(db: Session = Depends(get_db)):
    copies= db.query(ItemCopy).filter(ItemCopy.delete_status!= DeletionStatusEnum.DELETED).all()
    return copies

# 복사본 단일 조회
@router.get("/{copy_id}",response_model=ItemCopySchemas)
def get_copy(copy_id: int, db: Session = Depends(get_db)):
    copy = db.query(ItemCopy).filter(ItemCopy.copy_id == copy_id,ItemCopy.delete_status!= DeletionStatusEnum.DELETED).first()
    if not copy:
        raise HTTPException(status_code=404, detail="Copy not found")
    return copy

# 복사본 생성
@router.post("/", response_model=ItemCopyCreate)
def create_copy(data: ItemCopyCreate, db: Session = Depends(get_db)):
    copy = ItemCopy(**data.model_dump())
    db.add(copy)
    db.commit()
    db.refresh(copy)
    return copy

# 복사본 상태 변경
@router.patch("/{copy_id}/status", response_model=dict)
def update_copy_status(copy_id: int, data: ItemCopyUpdate, db: Session = Depends(get_db)):
    copy = db.query(ItemCopy).filter(ItemCopy.copy_id == copy_id, ItemCopy.delete_status!= DeletionStatusEnum.DELETED).first()
    if not copy:
        raise HTTPException(status_code=404, detail="Copy not found")
    copy.copy_status = data.copy_status
    db.commit()
    return {"success": True}

# 복사본 삭제 (소프트 삭제)
@router.post("/{copy_id}", response_model=dict)
def delete_copy(copy_id: int, db: Session = Depends(get_db)):
    copy = db.query(ItemCopy).filter(ItemCopy.delete_status!= DeletionStatusEnum.DELETED).first()
    if not copy:
        raise HTTPException(status_code=404, detail="Copy not found")
    db.delete(copy)
    db.commit()
    return {"success": True, "message": "Copy deleted"}
