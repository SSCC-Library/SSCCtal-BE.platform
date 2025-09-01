from fastapi import APIRouter, Depends,Query
from models.item import Item
from models.item_copy import ItemCopy
from database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional
from new_schemas.response import CommonResponse, ListItemWithCopyData,AdminItemMainInfo
from new_schemas.item_copy import ItemCopyMainInfo
from sqlalchemy import cast, String
from security import get_current_user


router = APIRouter(prefix="/items", tags=["items"])

size=12


@router.get("/list", response_model=CommonResponse[list[AdminItemMainInfo]])
async def get_items(
    page: int = Query(1, ge=1),
    token: int =Depends(get_current_user),
    search_type: Optional[str] = Query(None, description="검색 기준 (item_id, name, hashtag)"),
    search_text: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * size

    # JOIN: ItemCopy + Item
    query = db.query(Item)

    # Filtering
    if search_type and search_text:
        keyword = f"%{search_text}%"
        if search_type == "item_id":
            #item_id str로 변경,  keyword와 일치하는 부분 검색
            query = query.filter(cast(Item.item_id, String).ilike(keyword))
        elif search_type == "name":
            query = query.filter(Item.name.ilike(keyword))  #  keyword와 일치하는 부분 검색
        elif search_type == "hashtag":
            query = query.filter(Item.hashtag.ilike(keyword))  # keyword와 일치하는 부분 검색

    count = query.count()
    items = query.offset(offset).limit(size).all()

    if not items:
        return CommonResponse(
            success=False,
            code=404
        )

    data = [AdminItemMainInfo.model_validate(item) for item in items]

    return CommonResponse(
        success=True,
        code=200,
        data=data,
        total=count,
        page=page,
        size=size
    )
