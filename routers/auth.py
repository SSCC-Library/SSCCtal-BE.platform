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
    school_id: int = None
    token: str = None


# saint 실서비스 인증 (httpx 비동기 호출)
async def saint_auth(student_id: int, password: str) -> bool:
    url = "https://smartid.ssu.ac.kr/smln_pcs.asp"
    headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Referer": "https://smartid.ssu.ac.kr/Symtra_sso/smln.asp?apiReturnUrl=https%3A%2F%2Fsaint.ssu.ac.kr%2FwebSSO%2Fsso.jsp",
    "Origin": "https://smartid.ssu.ac.kr/",
    }
    data = {
        "in_tp_bit": "0",
        "rqst_caus_cd": "03",
        "userId": str(student_id),
        "pwd": password,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, headers=headers)
        return "parent.location.href" in response.text


# 로그인 엔드포인트
@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    if not await saint_auth(data.student_id, data.password):
        raise HTTPException(status_code=400, detail="saint 로그인 실패")

    user = db.query(User).filter(User.student_id == data.student_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="사용자 미등록")

    return LoginResponse(
        success=True,
        code=200,
        name=user.name,
        school_id=user.student_id,
        token="jwt-token-placeholder",  # JWT 연동 전까지는 placeholder
    )


# 로그아웃 엔드포인트
@router.post("/logout")
def logout():
    return {"success": True, "message": "로그아웃 완료"}
