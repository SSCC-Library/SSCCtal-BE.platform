from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.login import LoginRequest, LoginResponse
import httpx

router = APIRouter()


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
        s_token = response.cookies.get("sToken") # sToken 쿠키 

        return s_token


@router.post("/api/v1/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    s_token = await saint_auth(data.student_id, data.password)
    print(s_token)
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
        token="jwt-token-placeholder"
    )


@router.post("/api/v1/logout")
def logout():
    return {
        "success": True,
        "code": 200
    }
