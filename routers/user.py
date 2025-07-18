from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from models.rental import Rental
from models.item import Item
from models.item_copy import ItemCopy
from models.user import User
from models.user import User, UserStatusEnum, DeletionStatusEnum
from database import get_db
from schemas.user import UserBase, UserCreate, UserUpdate,PersonalRentalItem,PersonalRentalListResponse
from dependencies import hash_phone_number
from security import get_current_user
from new_schemas.response import CommonResponse
from new_schemas.rental import RentalMainInfo

router = APIRouter(prefix="/users", tags=["users"])

size = 12

@router.get("/me/rentals",response_model=CommonResponse[list[RentalMainInfo]])
def get_my_rentals(page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    student_id : Optional[int] = None, db: Session = Depends(get_db)) :

    query = (
        db.query(Rental)
        .join(ItemCopy, Rental.copy_id == ItemCopy.copy_id)
        .join(Item, ItemCopy.item_id == Item.item_id)
        .filter(Rental.student_id == student_id)
    )
    count=query.count()
    offset = (page - 1) * size
    rentals = query.offset(offset).limit(size).all()

    if not rentals:
        return CommonResponse(
        success= False,
        code= 404
        )
    
    result = []
    for rental in rentals:
       

        result.append(RentalMainInfo(
        rental_id=rental.rental_id,
        student_id=rental.student_id,
        rental_status=rental.rental_status,
        item_borrow_date=rental.item_borrow_date,
        expectation_return_date=rental.expectation_return_date,
        item_return_date=rental.item_return_date,
        overdue=rental.overdue
))
    return CommonResponse(
        success= True,
        code= 200,
        data= result,
        count=count,
        page= page,
        size= size
    )






# 전체 유저 목록 조회
@router.get("/v1/", response_model=List[UserBase])
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# 단일 유저 조회
@router.get("/search/{student_id}")
def search_users(
    student_id: Optional[int] = None,
    name: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(User).filter(User.user_status != UserStatusEnum.DELETED)

    if student_id:
        query = query.filter(User.student_id == student_id)
    if name:
        query = query.filter(User.name == name)
    if email:
        query = query.filter(User.email == email)

    results = query.all()

    if not results:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    return results

# 유저 생성 (테스트용)
@router.post("/v1", response_model=UserBase)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user = User(**user_data.model_dump())
    user.phone_number=hash_phone_number(user.phone_number)  #전화번호 해시
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# 유저 정보 업데이트  (기존 데이터를 보여줘야합니다)
@router.post("/v1/{student_id}", response_model=UserUpdate)
def update_user(student_id: int, update_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.student_id == student_id,
        User.user_status != UserStatusEnum.DELETED
        ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    user.phone_number=hash_phone_number(user.phone_number)  #전화번호 해시
    db.commit()
    db.refresh(user)
    return user


# 유저 삭제 (회원탈퇴 처리)
@router.post("/v1/{student_id}/delete")
def delete_user(student_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.student_id == student_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.delete_status = DeletionStatusEnum.DELETED.value
    db.commit()
    return {"success": True, "message": "User logically deleted"}
