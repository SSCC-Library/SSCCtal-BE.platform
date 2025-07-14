from fastapi import APIRouter, HTTPException,Depends,Query
from models.item import Item, ItemTypeEnum
from models.item_copy import ItemCopy,CopyStatusEnum
from database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional
from schemas.item import AdminItemListResponse,AdminItemSimple,ItemDetail,ItemCopyResponse
from new_schemas.response import CommonResponse, ItemWithItemCopyData,ListItemWithCopyData
from new_schemas.item import ItemMainInfo, AdminItemMainInfo
from new_schemas.item_copy import ItemCopyBase,ItemCopyMainInfo
from sqlalchemy import cast, String

router = APIRouter(prefix="/items", tags=["admin_items"])

size=12

@router.get("", response_model=CommonResponse[List[ListItemWithCopyData]])
def get_admin_items(
    page: int = Query(1, ge=1),
    search_type: Optional[str] = Query(None, description="검색 기준 (item_id, name, hashtag)"),
    search_text: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * size

    # JOIN: ItemCopy + Item
    query = db.query(ItemCopy, Item).join(Item, Item.item_id == ItemCopy.item_id)

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
        return CommonResponse(
            success=False,
            code=404,
            data=[],
            page=page,
            size=size
        )

    # 각 row는 (ItemCopy, Item) 튜플
    data: List[ListItemWithCopyData] = [
        ListItemWithCopyData(
            item_copy=ItemCopyMainInfo.model_validate(copy),
            item=ItemMainInfo.model_validate(item)
        )
        for copy, item in rows
    ]

    return CommonResponse(
        success=True,
        code=200,
        data=data,
        page=page,
        size=size
    )

@router.get("/{copy_id}", response_model=CommonResponse[ItemWithItemCopyData])
def get_item_copy(copy_id: int, db: Session = Depends(get_db)):
    copy = db.query(ItemCopy).filter(ItemCopy.copy_id == copy_id).first()
    if not copy:
        return ItemCopyResponse(success=False, code=404, item=None)

    item = db.query(Item).filter(Item.item_id == copy.item_id).first()
    if not item:
        return ItemCopyResponse(success=False, code=404, item=None)

    item_copy_data = ItemCopyBase(
        copy_id=copy.copy_id,
        item_id=copy.item_id,
        identifier_code=copy.identifier_code,
        copy_status=copy.copy_status,
        create_date=copy.create_date,
        update_date=copy.update_date,
        delete_status=copy.delete_status
    )

    item_data = AdminItemMainInfo(
        item_id=item.item_id,
        name=item.name,
        type=item.type,
        publisher=item.publisher,
        publish_date=item.publish_date,
        hashtag=item.hashtag,
        image_url=item.image_url,
        total_count=item.total_count,
        available_count=item.available_count
    )

    return CommonResponse(
        success=True,
        code=200,
        data=ItemWithItemCopyData(
            item=item_data,
            item_copy=item_copy_data
        )
    )
