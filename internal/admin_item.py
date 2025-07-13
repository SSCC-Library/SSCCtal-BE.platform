from fastapi import APIRouter, HTTPException,Depends,Query
from models.item import Item
from models.item_copy import ItemCopy
from database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional
from schemas.item import AdminItemListResponse,AdminItemSimple,ItemDetail,ItemCopyResponse
#from schemas.item_copy import ItemCopyResponse
from sqlalchemy import cast, String

router = APIRouter(prefix="/items", tags=["admin_items"])

size=12

@router.get("", response_model=AdminItemListResponse)
def get_admin_items(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
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

@router.get("/{copy_id}", response_model=ItemCopyResponse)
def get_item_copy(copy_id: int, db: Session = Depends(get_db)):
    copy = db.query(ItemCopy).filter(ItemCopy.copy_id == copy_id).first()
    if not copy:
        return ItemCopyResponse(success=False, code=404, item=None)

    item = db.query(Item).filter(Item.item_id == copy.item_id).first()
    if not item:
        return ItemCopyResponse(success=False, code=404, item=None)

    item_detail = ItemDetail(
    copy_id=copy.copy_id,
    item_id=copy.item_id,
    identifier_code=copy.identifier_code,
    copy_status=copy.copy_status.value,  # enum은 .value 꼭 써줘야 함
    create_date=copy.create_date,
    update_date=copy.update_date,
    name=item.name,
    type=item.type.value,
    publisher=item.publisher,
    publish_date=item.publish_date,
    hashtag=item.hashtag,
    image_url=item.image_url,
    total_count=item.total_count,
    available_count=item.available_count
)

    return ItemCopyResponse(
        success=True,
        code=200,
        item=item_detail  # ✅ 객체로 감싸기!
    )
