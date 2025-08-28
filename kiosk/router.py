from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from new_schemas.response import CommonResponse,KioskData
from sqlalchemy.orm import Session
from database import get_db
from models.rental import Rental,RentalStatusEnum
from models.item_copy import ItemCopy,CopyStatusEnum
from models.user import User
from models.item import Item
from dependencies import DeletionStatusEnum
from datetime import datetime, timedelta
from new_schemas.login import LoginResponse, LoginRequest
from new_schemas.item import ItemMainInfo
from new_schemas.item_copy import ItemCopyMainInfo
import httpx
from security import create_access_token,get_current_user


router = APIRouter(prefix="/kiosk", tags=["kiosk"])


async def saint_auth(student_id: int, password: str) -> str:
    url = "https://smartid.ssu.ac.kr/Symtra_sso/smln_pcs.asp"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://smartid.ssu.ac.kr/Symtra_sso/smln.asp?apiReturnUrl=https%3A%2F%2Fsaint.ssu.ac.kr%2FwebSSO%2Fsso.jsp",
    }
    data = {
        "in_tp_bit": "0",
        "rqst_caus_cd": "03",
        "userId": str(student_id),
        "pwd": password,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        response.raise_for_status()
        s_token = response.cookies.get("sToken") # sToken 쿠키 

        return s_token


@router.post("/login", response_model=CommonResponse[LoginResponse])
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    s_token = await saint_auth(data.student_id, data.password)
    if not s_token:
        return CommonResponse(success=False, code=400)   #비밀번호 불일치
    
    student_id = data.student_id
    user = db.query(User).filter(User.student_id == data.student_id).first()

    if not user:
        return CommonResponse(success=False, code=401)   #존재하지 않는 학번

    token = create_access_token({"student_id": user.student_id,"user_classification": user.user_classification.value.upper()})  # 학번 및 사용자 

    data=LoginResponse(token=token,name=user.name,student_id=user.student_id,user_classification=user.user_classification.value.upper())
 
    return CommonResponse(success=True, code=200, data=data)


@router.post("/logout")
def logout():
    return {
        "success": True,
        "code": 200
    }


@router.post("/rent", response_model=CommonResponse)
async def rent_item(
    isbn: str,
    student_id: int = Depends(get_current_user),
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
async def return_item(
    isbn: str,
    student_id: int = Depends(get_current_user),
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
    actual_return = datetime.now().date() # 현재 시간
    expected_return = rental.expectation_return_date  # 반납 예정일

    #날짜 비교
    if actual_return > expected_return:
        delta = actual_return - expected_return
        rental.overdue = delta.days

    rental.item_return_date = datetime.now()
    rental.rental_status=RentalStatusEnum.RETURNED  #rental 상태 수정
    item_copy.copy_status=CopyStatusEnum.AVAILABLE  #item_copy 테이블 해당 아이템 상태 가능 처리
    db.commit()

    return CommonResponse(success=True,code=200)

@router.get("/input/{isbn}",response_model=CommonResponse[KioskData])
async def check_item(isbn: str, student_id : str = Depends(get_current_user),db: Session = Depends(get_db)):
    item_copy_obj = db.query(ItemCopy).filter(ItemCopy.identifier_code == isbn).first()
    if not item_copy_obj:
        raise HTTPException(status_code=404, detail="해당 ISBN의 사본이 없습니다.")
    
    item_obj = db.query(Item).filter(Item.item_id == item_copy_obj.item_id).first()
    if not item_obj:
        raise HTTPException(status_code=404, detail="해당 아이템 정보가 없습니다.")

    item = ItemMainInfo.model_validate(item_obj)
    item_copy = ItemCopyMainInfo.model_validate(item_copy_obj)

    data = KioskData(item=item, item_copy=item_copy)

    return CommonResponse(success=True, code=200, data=data)
    
