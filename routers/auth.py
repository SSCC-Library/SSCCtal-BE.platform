"""
로그인 및 로그아웃 관련 엔드포인트 정의
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.user import User
import httpx

router = APIRouter()

# 로그인 요청 스키마
class LoginRequest(BaseModel):
    student_id: int
    password: str

# 로그인 응답 스키마
class LoginResponse(BaseModel):
    success: bool
    code: int
    name: str = None
    student_id: int = None
    token: str = None

# Saint 인증 함수
async def saint_auth(student_id: int, password: str) -> str:
    url = "https://smartid.ssu.ac.kr/Symtra_sso/smln_pcs.asp"
    headers = {
        "User-Agent": "",
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
        s_token = response.cookies.get("sToken") # sToken 쿠키 뽑기
        return s_token


# 로그인 엔드포인트
@router.post("/api/v0/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    s_token = await saint_auth(data.student_id, data.password)
    if not s_token:
        return LoginResponse(
            success=False,
            code=400
        )

    user = db.query(User).filter(User.student_id == data.student_id).first()
    if not user:
        return LoginResponse(
            success=False,
            code=401
        )

    return LoginResponse(
        success=True,
        code=200,
        name=user.name,
        student_id=user.student_id,
        token="jwt-token-placeholder",  # JWT 연동 전까지는 placeholder
    )


# 로그아웃 엔드포인트
@router.post("/api/v0/logout")
def logout():
    return {
        "success": True,
        "code": 200
    }
