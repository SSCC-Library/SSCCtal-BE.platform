from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from new_schemas.response import CommonResponse
from new_schemas.user import UserMainInfo,UserBase
from models.user import User
from models.user import User, UserStatusEnum, DeletionStatusEnum
from database import get_db
from dependencies import hash_phone_number,DeletionStatusEnum
from security import get_current_user,encrypt_phone,decrypt_phone

router = APIRouter(prefix="/users", tags=["admin_users"])

size =12

@router.get("", response_model=CommonResponse[List[UserMainInfo]])
def get_admin_users(
    page: int = Query(..., ge=1, description="페이지 번호 (1부터 시작)"),
    search_type: Optional[str] = Query(None, description="검색 기준 (student_id 또는 name)"),
    search_text: Optional[str] = Query(None, description="검색어"),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * size

    query = db.query(User).filter(User.delete_status != DeletionStatusEnum.DELETED)

    if search_type and search_text:
        if search_type == "student_id":
            query = query.filter(User.student_id == int(search_text))
        elif search_type == "name":
            query = query.filter(User.name.ilike(f"%{search_text}%"))

    total = query.count()
    users = query.offset(offset).limit(size).all()

    if not users:
        return CommonResponse(success=False, code=404, total=0, page=page, size=size)

    user_list = []
    for user in users:
        phone = decrypt_phone(user.phone_number)  # 전화번호 복호화

        user_list.append(UserMainInfo.model_validate(user)  
        )
        '''
        student_id=user.student_id,
        name=user.name,
        email=user.email,
        phone_number=phone,
        gender=user.gender,
        major=user.major,
        major2=user.major2,
        minor=user.minor,
        user_classification=user.user_classification
        '''

    return CommonResponse(
        success=True,
        code=200,
        data=user_list,
        total=total,
        page=page,
        size=size
    ) 

# 단일 유저 조회
@router.get("/search/{student_id}",response_model=CommonResponse[UserBase])
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
        return CommonResponse(
            success=False,
            code=404
        )
    decrypted_phone = decrypt_phone(user.phone_number)  #전화번호 복호화
    '''
    user_data = UserBase(
        id=user.id,
        student_id=user.student_id,
        name=user.name,
        email=user.email,
        phone_number=decrypted_phone,
        gender=user.gender,
        major=user.major,
        major2=user.major2,
        minor=user.minor,
        user_classification=user.user_classification,
        join_date=user.join_date,
        update_date=user.update_date,
        user_status=user.user_status,
        delete_status=user.delete_status
    )
    '''
    user_data = UserBase.model_validate(user)  #user 데이터(ORM 객체)를 pydantic 모델로 생성
    user_data.phone_number = decrypted_phone
    return CommonResponse(
        success=True,
        code=200,
        data=user_data
    )

# 유저 생성 (테스트용)
@router.post("/create", response_model=CommonResponse)
def create_user(user_data: UserMainInfo, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | 
        (User.student_id == user_data.student_id) &
        (User.delete_status != DeletionStatusEnum.DELETED)
    ).first()
    
    if existing_user:
        return CommonResponse(success = False, code= 503)
    user = User(**user_data.model_dump())
    user.phone_number = encrypt_phone(user.phone_number)  #전화번호 암호화
    print(user.phone_number)
    db.add(user)
    db.commit()
    db.refresh(user)
    return CommonResponse(success = True, code= 200)



# 유저 정보 업데이트  (기존 데이터를 보여줘야합니다)
@router.post("/update/{student_id}",response_model=CommonResponse)
def update_user(student_id: int, update_data: UserMainInfo, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.student_id == student_id,
        User.user_status != UserStatusEnum.DELETED
        ).first()
    if not user:
        return CommonResponse(success = False, code= 503)

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    user.phone_number=encrypt_phone(user.phone_number)  #전화번호 해시
    db.commit()
    db.refresh(user)
    return CommonResponse(success = True, code= 200)


# 유저 삭제 (회원탈퇴 처리, 실제 삭제 x)
@router.post("/delete/{student_id}",response_model=CommonResponse)
def delete_user(student_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.student_id == student_id,
        User.delete_status != UserStatusEnum.DELETED).first()
    
    if not user:
        return CommonResponse(success = False, code= 503)
    
    user.delete_status = DeletionStatusEnum.DELETED.value
    db.commit()
    return CommonResponse(success = True, code= 200)
