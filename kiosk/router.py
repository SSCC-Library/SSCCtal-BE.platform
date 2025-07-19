from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
#from security import get_current_user
from new_schemas.response import CommonResponse
from sqlalchemy.orm import Session
from database import get_db
from models.rental import Rental,RentalStatusEnum
from models.item_copy import ItemCopy,CopyStatusEnum
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
            ItemCopy.delete_status != DeletionStatusEnum.DELETED,
            ItemCopy.copy_status == CopyStatusEnum.AVAILABLE
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
    copy.copy_status = CopyStatusEnum.BORROWED
    db.add(rental)
    db.commit()
    db.refresh(rental)

    return CommonResponse(success=True, code=200)


@router.post("/return", response_model=CommonResponse)
def return_item(
    isbn: str,
    student_id: int,
    db: Session = Depends(get_db)
):
    # Step 1: item_copy에서 ISBN에 해당하는 copy_id 조회
    item_copy = db.query(ItemCopy).filter(ItemCopy.identifier_code == isbn,
        ItemCopy.copy_status == CopyStatusEnum.BORROWED,
        ItemCopy.delete_status!=DeletionStatusEnum.DELETED).first()
    if not item_copy:
        return CommonResponse(success=False, code=404)

    # Step 2: rental 테이블에서 해당 copy_id와 student_id로 대여 기록 조회
    rental = (
        db.query(Rental)
        .filter(
            Rental.copy_id == item_copy.copy_id,
            Rental.student_id == student_id,
            Rental.rental_status==RentalStatusEnum.BORROWED
        )
        .first()
    )
    if not rental:
        return CommonResponse(success=False, code=404)

    # Step 3: 반납 처리
        #rental.item_return_date = True
    actual_return = datetime.now().date()
    expected_return = rental.expectation_return_date

    if actual_return > expected_return:
        delta = actual_return - expected_return
        rental.overdue = delta.days
    rental.item_return_date = datetime.now()
    rental.rental_status=RentalStatusEnum.RETURNED
    item_copy.copy_status=CopyStatusEnum.AVAILABLE
    db.commit()

    return CommonResponse(success=True,code=200)
