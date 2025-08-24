import os
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
from database import get_db
from models.user import User,UserClassificationEnum

# .env 파일에서 환경변수 불러오기
load_dotenv()


SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        student_id = payload.get("student_id")
        user_classification: str = payload.get("user_classification")



        if student_id is None:
            raise HTTPException(status_code=401, detail="토큰이 유효하지 않습니다.")
        
        if user_classification != "STAFF" or user_classification != "STUDENT":
            raise HTTPException(status_code=403, detail="권한이 없습니다.")
        
        return student_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_admin_user(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        student_id: int = payload.get("student_id")
        user_classification: str = payload.get("user_classification")

        if student_id is None or user_classification is None:
            raise HTTPException(status_code=401, detail="토큰이 유효하지 않습니다.")

        if user_classification != "STAFF":
            raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다.")

        return student_id

    except JWTError:
        raise HTTPException(status_code=401, detail="토큰 디코딩 실패")


FERNET_SECRET_KEY=os.environ.get("FERNET_SECRET_KEY")

cipher = Fernet(FERNET_SECRET_KEY)

def encrypt_phone(phone: str) -> str:
    return cipher.encrypt(phone.encode()).decode()

def decrypt_phone(encrypted: str) -> str:
    return cipher.decrypt(encrypted.encode()).decode()