import os
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# .env 파일에서 환경변수 불러오기
load_dotenv()


SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        student_id = payload.get("student_id")
        if student_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return student_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

FERNET_SECRET_KEY=os.environ.get("FERNET_SECRET_KEY")

cipher = Fernet(FERNET_SECRET_KEY)

def encrypt_phone(phone: str) -> str:
    return cipher.encrypt(phone.encode()).decode()

def decrypt_phone(encrypted: str) -> str:
    return cipher.decrypt(encrypted.encode()).decode()