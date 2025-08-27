from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import String
from database import get_db
from new_schemas.item import ItemMainInfo
from new_schemas.user import UserSimpleInfo
from new_schemas.rental import RentalMainInfo,RentalBase
from new_schemas.response import CommonResponse, RentalWithUserData,RentalStatusUpdate
from models.user import User
from models.rental import Rental,RentalStatusEnum
from models.item import Item
from models.item_copy import ItemCopy
from security import get_current_user,get_admin_user


router = APIRouter(prefix="/rentals", tags=["admin_rentals"])


size = 12
@router.get("", response_model=CommonResponse[List[RentalWithUserData]])
def get_admin_rentals(
    token : int =Depends(get_admin_user),
    page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    search_type: Optional[str] = Query(None, description="검색 기준 rental_id,student_id, name ,item_borrow_date, item_return_date, rental_status"),
    search_text: Optional[str] = Query(None, description="검색어"),
    rental_status: Optional[RentalStatusEnum] = Query(None, description="대여 상태 필터 (borrowed, returned, overdue)"),
    db: Session = Depends(get_db)
):
    
    offset = (page - 1) * size

    query = db.query(Rental) \
        .join(User, User.student_id == Rental.student_id) \
        .join(ItemCopy, Rental.copy_id == ItemCopy.copy_id) \
        .join(Item, ItemCopy.item_id == Item.item_id)

    if search_type and search_text:
        if search_type == "rental_id":
            query = query.filter(Rental.rental_id == int(search_text))
        elif search_type == "student_id":
            query = query.filter(User.student_id == int(search_text))
        elif search_type == "user_name":
            query = query.filter(User.name.ilike(f"%{search_text}%"))
        elif search_type == "item_borrow_date":
            query = query.filter(Rental.item_borrow_date.cast(String).ilike(f"%{search_text}%"))
        elif search_type == "item_return_date":
            query = query.filter(Rental.item_return_date.cast(String).ilike(f"%{search_text}%"))
        elif search_type == "rental_status":
            query = query.filter(Rental.rental_status.ilike(f"%{search_text}%"))
        elif search_type == "type":
            query = query.filter(Item.type.ilike(f"%{search_text}%"))
        elif search_type == "name":
            query = query.filter(Item.name.ilike(f"%{search_text}%"))

    if rental_status:
        query = query.filter(Rental.rental_status == rental_status)

    count = query.count()
    rentals = query.offset(offset).limit(size).all()

    if not rentals:
        return CommonResponse(success=False, code=404)

    results = []
    for rental in rentals:
        rental_data = RentalMainInfo.model_validate(rental)
        '''
        rental_data = RentalMainInfo(
            rental_id=rental.rental_id,
            student_id=rental.student_id,
            rental_status=rental.rental_status,
            item_borrow_date=rental.item_borrow_date,
            expectation_return_date=rental.expectation_return_date,
            item_return_date=rental.item_return_date,
            overdue=rental.overdue
        )
        '''

        user_data = UserSimpleInfo(
            student_id=rental.user.student_id,
            name=rental.user.name
        )

        item_data = ItemMainInfo(
        name=rental.item_copy.item.name,
        type=rental.item_copy.item.type
        )

        results.append(RentalWithUserData(user=user_data, rental=rental_data, item=item_data))

    return CommonResponse(
        success=True,
        code=200,
        data=results,
        total=count,
        page=page,
        size=size
    )

# rental 상세 정보 조회
@router.get("/{rental_id}", response_model=CommonResponse[RentalBase])
def get_rental_by_id(rental_id: int, token : int =Depends(get_admin_user), db: Session = Depends(get_db)):
    rental = db.query(Rental).filter(Rental.rental_id == rental_id).first()
    
    if not rental:
        CommonResponse(success=False,code=404)

    return CommonResponse(success=True,code=200,data=rental)

# rental 기록 업데이트
@router.post("/{rental_id}", response_model=CommonResponse)
def update_rental_main_info(
    rental_id: int,
    data: RentalMainInfo,
    token : int =Depends(get_admin_user),
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

# rental 상태 변경
@router.post("/status/{rental_id}", response_model=CommonResponse)
def rental_status_info(rental_id: int,
    rental_status: RentalStatusUpdate,
    token : int =Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    rental = db.query(Rental).filter(Rental.rental_id == rental_id).first()

    if not rental:
        return CommonResponse(success=False, code=404)

    rental.rental_status = rental_status.rental_status
    db.commit()
    db.refresh(rental)
    print("변경된 상태:", rental.rental_status)
    return CommonResponse(success=True, code=200)