from fastapi import APIRouter,Depends,Query
from models.item import Item, ItemTypeEnum
from models.item_copy import ItemCopy, CopyStatusEnum
from database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional
from new_schemas.response import CommonResponse, ItemWithItemCopyData,ListItemWithCopyData
from new_schemas.item import ItemMainInfo, AdminItemMainInfo
from new_schemas.item_copy import ItemCopyBase,ItemCopyMainInfo,CopyStatusEnum
from sqlalchemy import cast, String
from dependencies import DeletionStatusEnum
from services.item_service import fetch_book_info
from datetime import datetime
from security import get_admin_user

router = APIRouter(prefix="/items", tags=["admin_items"])

size=12

@router.get("", response_model=CommonResponse[List[ListItemWithCopyData]])
def get_admin_items(
    token : int =Depends(get_admin_user),
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
        if search_type == "copy_id":
            query = query.filter(cast(Item.item_id, String).ilike(keyword))
        elif search_type == "name":
            query = query.filter(Item.name.ilike(keyword))
        elif search_type == "hashtag":
            query = query.filter(Item.hashtag.ilike(keyword))

    count=query.count()
    rows = query.offset(offset).limit(size).all()
    
    if not rows:
        return CommonResponse(
            success=False,
            code=404,
            page=page,
            size=size
        )

    # 각 row는 (ItemCopy, Item) 튜플
    data: List[ListItemWithCopyData] = [
        ListItemWithCopyData(
            item_copy=ItemCopyMainInfo.model_validate(copy),
            item=AdminItemMainInfo.model_validate(item)
        )
        for copy, item in rows
    ]

    return CommonResponse(
        success=True,
        code=200,
        data=data,
        total=count,
        page=page,
        size=size
    )

@router.get("/{copy_id}", response_model=CommonResponse[ItemWithItemCopyData])
def get_item_copy(copy_id: int,db: Session = Depends(get_db)):
    copy = db.query(ItemCopy).filter(ItemCopy.copy_id == copy_id).first()
    if not copy:
        return CommonResponse(success=False, code=404)

    item = db.query(Item).filter(Item.item_id == copy.item_id).first()
    if not item:
        return CommonResponse(success=False, code=404)

    item_copy_data = ItemCopyBase.model_validate(copy)

    item_data = AdminItemMainInfo.model_validate(item)

    return CommonResponse(
        success=True,
        code=200,
        data=ItemWithItemCopyData(
            item=item_data,
            item_copy=item_copy_data
        )
    )

#, token : str =Depends(get_admin_user)
@router.post("/add",response_model= CommonResponse)
def add_items(isbn: str,db: Session = Depends(get_db)):

    # 1. 기존 item 조회
    item = db.query(Item).filter(
        Item.identifier_code == isbn,
        Item.delete_status != DeletionStatusEnum.DELETED
    ).first()

    if item:
        # 2. 존재할 경우: 수량 +1 증가
        item.total_count += 1
        item.available_count += 1
        item.update_date = datetime.utcnow()

        # 3. 복사본 추가
        new_copy = ItemCopy(
            item_id=item.item_id,
            identifier_code=isbn,
            copy_status=CopyStatusEnum.AVAILABLE,
            create_date=datetime.utcnow(),
            update_date=datetime.utcnow(),
            delete_status=DeletionStatusEnum.ACTIVE
        )
        db.add(new_copy)
        db.commit()
        return CommonResponse(success=True, code=200)

    # 4. 존재하지 않을 경우: YES24에서 정보 가져오기
    info = fetch_book_info(isbn)
    if not info:
        raise CommonResponse(success=False,code=404)

    # 5. 새 item 추가
    new_item = Item(
        identifier_code=info['identifier_code'],
        name=info['name'],
        type=ItemTypeEnum.BOOK,
        publisher=info['publisher'],
        publish_date=info['publish_date'],
        image_url=info['image_url'],
        total_count=1,
        available_count=1,
        create_date=datetime.utcnow(),
        update_date=datetime.utcnow(),
        delete_status=DeletionStatusEnum.ACTIVE
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    # 6. 복사본 추가
    new_copy = ItemCopy(
        item_id=new_item.item_id,
        identifier_code=isbn,
        copy_status=CopyStatusEnum.AVAILABLE,
        create_date=datetime.utcnow(),
        update_date=datetime.utcnow(),
        delete_status=DeletionStatusEnum.ACTIVE
    )
    db.add(new_copy)
    db.commit()
    return CommonResponse(success=True, code=200)

