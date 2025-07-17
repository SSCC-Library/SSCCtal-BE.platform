from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
#from security import get_current_user
from new_schemas.response import CommonResponse
from sqlalchemy.orm import Session
from database import get_db
from models.rental import Rental,RentalStatusEnum
from models.item_copy import ItemCopy
from dependencies import DeletionStatusEnum
from datetime import datetime, timedelta

router = APIRouter(prefix="/kiosk", tags=["kiosk"])


@router.post("/rent", response_model=CommonResponse)
def rent_item(
    isbn: str,
    student_id: int,
    db: Session = Depends(get_db)
):
    copy = (
        db.query(ItemCopy)
        .filter(
            ItemCopy.identifier_code == isbn,
            ItemCopy.delete_status != DeletionStatusEnum.DELETED
        )
        .first()
    )

    if not copy:
        return CommonResponse(success=False, code=404, message="대여 가능한 복사본이 없습니다.")

    # 2. 대여 등록
    rental = Rental(
        student_id=student_id,
        copy_id=copy.copy_id,
        rental_status=RentalStatusEnum.BORROWED,
        item_borrow_date=datetime.now(),
        expectation_return_date=datetime.now().date() + timedelta(days=7),
        item_return_date=None,
        overdue=0,
        create_date=datetime.now(),
        update_date=datetime.now(),
        delete_status=DeletionStatusEnum.ACTIVE
    )

    db.add(rental)
    db.commit()
    db.refresh(rental)

    return CommonResponse(success=True, code=200)


@router.post("/rent", response_model=CommonResponse)
def return_item(
    isbn: str,
    student_id: int,
    db: Session = Depends(get_db)
):
    copy = (
        db.query(Rental)
        .filter(
            Rental.identifier_code == isbn,
            ItemCopy.delete_status != DeletionStatusEnum.DELETED
        )
        .first()
    )

    if not copy:
        return CommonResponse(success=False, code=404, message="대여 가능한 복사본이 없습니다.")