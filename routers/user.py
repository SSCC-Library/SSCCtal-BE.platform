from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from models.rental import Rental
from models.item import Item
from models.item_copy import ItemCopy
from database import get_db
from new_schemas.response import CommonResponse
from new_schemas.rental import RentalMainInfo,RentalMainInfoWithItem
from new_schemas.user import UserMainInfo


router = APIRouter(prefix="/users", tags=["users"])

size = 12

@router.get("/items/rental-records",response_model=CommonResponse[list[RentalMainInfoWithItem]])
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
        rental_info = RentalMainInfo.model_validate(rental, from_attributes=True)
        result.append(RentalMainInfoWithItem(rental=rental_info,
                                             item_name=rental.item_copy.item.name))

    return CommonResponse(
        success= True,
        code= 200,
        data= result,
        total=count,
        page= page,
        size= size
    )

'''

@router.post("/create", response_model=CommonResponse)
def create_user(user_data: UserMainInfo, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.student_id == user_data.student_id)
    ).first()

    if existing_user:
        return CommonResponse(success=False, code=503, message="이미 존재하는 사용자입니다.")

    user = User(**user_data.model_dump())
    user.phone_number = encrypt_phone(user.phone_number)  # 🔐 전화번호 암호화

    db.add(user)
    db.commit()
    db.refresh(user)

    return CommonResponse(success=True, code=200, message="사용자 생성 완료")


# 전체 유저 목록 조회
@router.get("/v1/", response_model=List[UserBase])
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


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
'''