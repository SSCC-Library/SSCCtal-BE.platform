from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from schemas.user import UserResponse
from models.user import User
from models.user import User, UserStatusEnum, DeletionStatusEnum
from database import get_db
from schemas.user import UserBase, UserCreate, UserUpdate,UsersBase,UsersResponse
from dependencies import hash_phone_number
from security import get_current_user

router = APIRouter(prefix="/users", tags=["admin_users"])

# 전체 유저 목록 조회
@router.get("/")
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"success" : True, "code" :200, "users" : users, "page" : 2}

    

# 단일 유저 조회
@router.get("/search/{student_id}")
def search_users(
    student_id: Optional[int] = None,
    name: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(User).filter(User.user_status != UserStatusEnum.DELETED)

    if student_id is not None:
        query = query.filter(User.student_id == student_id)
    if name:
        query = query.filter(User.name == name)
    if email:
        query = query.filter(User.email == email)

    user = query.first()

    if not user:
        return UserResponse(
            success=False,
            code=404
        )
    
    return UserResponse(
        success=True,
        code=200,
        user=user
    )

# 유저 생성 (테스트용)
@router.post("/create")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.student_id == user_data.student_id)
    ).first()
    
    if existing_user:
        return {"success" : False, "code" :503}
    user = User(**user_data.model_dump())
    user.phone_number=hash_phone_number(user.phone_number)  #전화번호 해시
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"success" : True, "code" :200}

# 유저 정보 업데이트  (기존 데이터를 보여줘야합니다)
@router.post("/update/{student_id}")
def update_user(student_id: int, update_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.student_id == student_id,
        User.user_status != UserStatusEnum.DELETED
        ).first()
    if not user:
        return {"success" : False, "code" :503}

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    user.phone_number=hash_phone_number(user.phone_number)  #전화번호 해시
    db.commit()
    db.refresh(user)
    return {"success" : True, "code" :200}


# 유저 삭제 (회원탈퇴 처리)
@router.post("/delete/{student_id}")
def delete_user(student_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.student_id == student_id,
        User.delete_status != UserStatusEnum.DELETED).first()
    
    if not user:
        return {"success" : False, "code" :503} 
    
    user.delete_status = DeletionStatusEnum.DELETED.value
    db.commit()
    return {"success" : True, "code" :200}
