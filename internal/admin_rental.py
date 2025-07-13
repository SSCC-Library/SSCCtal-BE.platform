from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from new_schemas.user import UserSimpleInfo
from new_schemas.rental import RentalMainInfo,RentalBase
from schemas.response import CommonResponse, RentalWithUserData
from models.user import User
from models.rental import Rental,RentalStatusEnum


router = APIRouter(prefix="/rentals", tags=["admin_rentals"])


size = 12
@router.get("", response_model=CommonResponse[List[RentalWithUserData]])
def get_admin_rentals(
    page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    search_type: Optional[str] = Query(None, description="검색 기준 (student_id 또는 name)"),
    search_text: Optional[str] = Query(None, description="검색어"),
    rental_status: Optional[RentalStatusEnum] = Query(None, description="대여 상태 필터 (borrowed, returned, overdue)"),
    db: Session = Depends(get_db)
):
    size = 10
    offset = (page - 1) * size

    query = db.query(Rental).join(User, User.student_id == Rental.student_id)

    if search_type and search_text:
        if search_type == "student_id":
            query = query.filter(User.student_id == int(search_text))
        elif search_type == "name":
            query = query.filter(User.name.ilike(f"%{search_text}%"))

    # 🔍 rental_status 필터링 추가
    if rental_status:
        query = query.filter(Rental.rental_status == rental_status)

    rentals = query.offset(offset).limit(size).all()

    if not rentals:
        return CommonResponse(success=False, code=404)

    results = []
    for rental in rentals:
        rental_data = RentalMainInfo(
            rental_id=rental.rental_id,
            student_id=rental.student_id,
            rental_status=rental.rental_status,
            item_borrow_date=rental.item_borrow_date,
            expectation_return_date=rental.expectation_return_date,
            item_return_date=rental.item_return_date,
            overdue=rental.overdue
        )
        user_data = UserSimpleInfo(
            student_id=rental.user.student_id,
            name=rental.user.name
        )
        results.append(RentalWithUserData(user=user_data, rental=rental_data))

    return CommonResponse(
        success=True,
        code=200,
        data=results
    )


@router.get("/{rental_id}", response_model=CommonResponse[RentalBase])
def get_rental_by_id(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(Rental).filter(Rental.rental_id == rental_id).first()
    
    if not rental:
        CommonResponse(success=False,code=404)

    return CommonResponse(success=True,code=200,data=rental)


@router.post("/update/{rental_id}", response_model=CommonResponse)
def update_rental_main_info(
    rental_id: int,
    data: RentalMainInfo,
    db: Session = Depends(get_db)
):
    rental = db.query(Rental).filter(Rental.rental_id == rental_id).first()

    if not rental:
        CommonResponse(success=False,code=404)

    for field, value in data.dict(exclude_none=True).items():
        setattr(rental, field, value)

    db.commit()
    db.refresh(rental)

    return CommonResponse(success=True,code=200)