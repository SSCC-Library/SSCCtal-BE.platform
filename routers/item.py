from fastapi import APIRouter, HTTPException,Depends,Query
from models.item import Item
from models.item_copy import ItemCopy
from database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional
from schemas.item import ItemCreate, ItemBase, ItemListResponse, AdminItemSimple,AdminItemListResponse
from dependencies import DeletionStatusEnum
from sqlalchemy import cast, String

router = APIRouter(prefix="/items", tags=["items"])

size=12


@router.get("/user", response_model=AdminItemListResponse)
def get_admin_items(
    page: int = Query(1, ge=1),
    search_type: Optional[str] = Query(None),
    search_text: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * size

    # Base query with join
    query = db.query(
        ItemCopy.copy_id,
        ItemCopy.item_id,
        ItemCopy.copy_status,
        Item.identifier_code,
        Item.name,
        Item.type,
        Item.hashtag
    ).join(Item, Item.item_id == ItemCopy.item_id)

    # Filtering
    if search_type and search_text:
        keyword = f"%{search_text}%"
        if search_type == "item_id":
            query = query.filter(cast(Item.item_id, String).ilike(keyword))
        elif search_type == "name":
            query = query.filter(Item.name.ilike(keyword))
        elif search_type == "hashtag":
            query = query.filter(Item.hashtag.ilike(keyword))

    total = query.count()
    rows = query.offset(offset).limit(size).all()

    if not rows:
        return AdminItemListResponse(success=False, code=404)

    items = [
        AdminItemSimple(
            copy_id=row.copy_id,
            item_id=row.item_id,
            copy_status=row.copy_status,
            identifier_code=row.identifier_code,
            name=row.name,
            type=row.type,
            hashtag=row.hashtag
        )
        for row in rows
    ]

    return AdminItemListResponse(
        success=True,
        code=200,
        items=items,
        total=total,
        page=page,
        size=size
    )
'''
@router.get("/admin", response_model=AdminItemListResponse)
def get_items_with_copy_info(
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(Item).filter(Item.delete_status != DeletionStatusEnum.DELETED)


    items = query.offset((page - 1) * size).limit(size).all()

    result = []
    for item in items:
        # 복수의 복사본이 있을 수 있음
        for copy in item.copies:
            result.append({
                "item_id": item.item_id,
                "name": item.name,
                "type": item.type,
                "copy_status": copy.copy_status,
                "identifier_code": copy.identifier_code,
                "hashtag": item.hashtag
            })

    return {
        "success": True,
        "code": 200,
        "items": result,
        "page": page,
        "size": size
    }


#아이템 목록 전체 조회
@router.get("/", response_model=List[ItemCreate])
def get_items(db: Session = Depends(get_db)):
    items = db.query(Item).filter(Item.delete_status!= DeletionStatusEnum.DELETED).all()
    return items

#운영자 아이템 개별 조회
@router.get("/admin/{item_id}", response_model=AdminItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.item_id == item_id,Item.delete_status!= DeletionStatusEnum.DELETED).first()
    if not item:
        return {
        "success": False,
        "code": 404,
        "data": item  # 여기서 기존 Item Pydantic 스키마로 자동 변환됨
    }
    return {
        "success": True,
        "code": 200,
        "data": item  # 여기서 기존 Item Pydantic 스키마로 자동 변환됨
    }

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
    '''