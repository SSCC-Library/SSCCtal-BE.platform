from fastapi import APIRouter, Depends,HTTPException,Query
from sqlalchemy.orm import Session
from database import get_db
from models.user import User,UserClassificationEnum
from new_schemas.login import LoginRequest, LoginResponse
import httpx
from security import create_access_token,get_current_user
from new_schemas.response import CommonResponse

router = APIRouter(prefix="/auth", tags=["_auth"])


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

    token = create_access_token({"student_id": user.student_id,"user_classification": user.user_classification.value})  # 학번 및 사용자 

    data=LoginResponse(token=token,name=user.name,student_id=user.student_id)
    print
    return CommonResponse(success=True, code=200, data=data)


@router.post("/logout")
def logout():
    return {
        "success": True,
        "code": 200
    }

