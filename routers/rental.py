from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import get_db
from models.rental import Rental, RentalStatusEnum
from models.item import ItemCopy, Copy_StatusEnum
from schemas.rental import RentalBase, RentalCreate, RentalUpdate
from dependencies import DeletionStatusEnum, korea_time, seven_days_later

router = APIRouter(prefix="/rentals", tags=["rentals"])


class RentalRequest(BaseModel):
    student_id: int
    copy_id: int
    rental_classification: str


# 전체 대여 내역 조회 (필터 포함)
@router.get("/v0/list", response_model=List[RentalBase])
def list_rentals(
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


#  단일 대여 조회
@router.get("/v0/{rental_id}", response_model=RentalBase)
def get_rental(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(Rental).filter(Rental.rental_id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="대여 기록이 없습니다.")
    return rental


#  대여 생성
@router.post("/v0/add", response_model=RentalBase)
def create_rental(data: RentalRequest, db: Session = Depends(get_db)):
    copy = db.query(ItemCopy).filter(
        ItemCopy.copy_id == data.copy_id,
        ItemCopy.delete_status == DeletionStatusEnum.ACTIVE
    ).first()

    if not copy:
        raise HTTPException(status_code=404, detail="해당 복사본이 존재하지 않습니다.")
    
    if copy.copy_status != Copy_StatusEnum.AVAILABLE:
        raise HTTPException(status_code=400, detail="복사본이 대여 불가능한 상태입니다.")

    # 복사본 상태를 대여중으로 업데이트
    copy.copy_status = Copy_StatusEnum.BORROWED

    # Rental 생성
    rental = Rental(
        student_id=data.student_id,
        copy_id=data.copy_id,
        copy_status=RentalStatusEnum.BORROWED,
        item_borrow_date=korea_time(),
        expectation_return_date=seven_days_later(),
        overdue=0
    )

    db.add(rental)
    db.commit()
    db.refresh(rental)

    return rental


#  대여 정보 수정 (간단한 필드만 예시로 수정)
@router.post("/v0/{rental_id}/edit", response_model=RentalBase)
def update_rental(rental_id: int, data: RentalUpdate, db: Session = Depends(get_db)):
    rental = db.query(Rental).filter(Rental.rental_id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=404, detail="대여 기록이 없습니다.")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(rental, field, value)

    db.commit()
    db.refresh(rental)
    return rental


# 대여 삭제 (soft delete)
@router.post("/v0/{rental_id}")
def delete_rental(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(Rental).filter(
        Rental.rental_id == rental_id,
        Rental.delete_status == DeletionStatusEnum.ACTIVE
    ).first()

    if not rental:
        raise HTTPException(status_code=404, detail="삭제할 대여 기록이 없습니다.")

    rental.delete_status = DeletionStatusEnum.DELETED
    db.commit()
    return {"success": True, "message": "대여 기록이 삭제(soft)되었습니다."}


# 대여 반납 처리
@router.post("/v0/{rental_id}/return", response_model=RentalUpdate)
def return_rental(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(Rental).filter(
        Rental.rental_id == rental_id,
        Rental.delete_status == DeletionStatusEnum.ACTIVE
    ).first()

    if not rental:
        raise HTTPException(status_code=404, detail="대여 기록을 찾을 수 없습니다.")
    if rental.item_return_date:
        raise HTTPException(status_code=400, detail="이미 반납된 대여 기록입니다.")

    # 복사본 상태를 'AVAILABLE'로 변경
    copy = db.query(ItemCopy).filter(ItemCopy.copy_id == rental.copy_id).first()
    if not copy:
        raise HTTPException(status_code=404, detail="연결된 복사본을 찾을 수 없습니다.")

    copy.copy_status = Copy_StatusEnum.AVAILABLE
    rental.item_return_date = datetime.now()
    rental.copy_status=RentalStatusEnum.RETURNED
    db.commit()
    db.refresh(rental)
    return rental