from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import get_db
from models.rental import Rental, RentalStatusEnum
from models.item_copy import ItemCopy, CopyStatusEnum
from schemas.rental import RentalBase, RentalUpdate, RentalItemResponse, RentalListResponse
from dependencies import DeletionStatusEnum, korea_time, seven_days_later
from schemas.response import CommonResponse

router = APIRouter(prefix="/rentals", tags=["admin_rentals"])


size = 12
@router.get("", response_model=CommonResponse[list[RentalBase]]) #개인 구부jwt 로직 추가 필요

def get_rentals(
    page: int = Query(1, ge=1, description="페이지 번호"),
    rental_status: Optional[RentalStatusEnum] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Rental).join(Rental.item_copy).join(ItemCopy.item)

    # 상태 필터
    if rental_status == RentalStatusEnum.BORROWED:
        query = query.filter(Rental.item_return_date == None, Rental.overdue == 0)
    elif rental_status == RentalStatusEnum.RETURNED:
        query = query.filter(Rental.item_return_date != None)
    elif rental_status == RentalStatusEnum.OVERDUE:
        query = query.filter(Rental.overdue > 0)

    rentals = query.offset((page - 1) * size).limit(size).all()

    if not rentals:
        return RentalListResponse(success=False, code=404)



    rental_items = [
        RentalItemResponse(
            name=r.item_copy.item.name,
            status=rental_status,
            item_borrow_date=r.item_borrow_date,
            expectation_return_date=r.expectation_return_date,
            item_return_date=r.item_return_date,
            overdue=r.overdue or 0
        ) for r in rentals
    ]

    return CommonResponse(
        success=True,
        code=200,
        items=rental_items,
        page=page,
        size=size
    )