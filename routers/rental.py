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


router = APIRouter(prefix="/rentals", tags=["rentals"])


class RentalRequest(BaseModel) :
    student_id : int
    copy_id : int

@router.get("/user", response_model=RentalListResponse) #개인 구부jwt 로직 추가 필요
async def get_rentals(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지당 개수"),
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

    return RentalListResponse(
        success=True,
        code=200,
        items=rental_items,
        page=page,
        size=size
    )

# 전체 대여 내역 조회 (필터 포함, 특정 사람 기준)
@router.get("/{student_id}", response_model=List[RentalBase])
async def list_rentals(
    student_id: Optional[int] = None,
    status: Optional[RentalStatusEnum] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Rental)

    if student_id:
        query = query.filter(Rental.student_id == student_id)

    if status == RentalStatusEnum.BORROWED:
        query = query.filter(Rental.item_return_date == None, Rental.overdue == 0)
    elif status == RentalStatusEnum.RETURNED:
        query = query.filter(Rental.item_return_date != None)
    elif status == RentalStatusEnum.OVERDUE:
        query = query.filter(Rental.overdue > 0)

    rentals = query.all()
    if not rentals:
        raise HTTPException(status_code=404, detail="대여 내역이 없습니다.")

    return rentals
