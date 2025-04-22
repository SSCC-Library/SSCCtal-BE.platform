"""
DB 연결 설정
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# .env 파일에서 환경변수 불러오기
load_dotenv()

# 환경변수에서 DB 연결 정보 가져오기
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")

# SQLAlchemy용 DB 연결 URL 생성
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

#DB 엔진 및 세션 설정
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 (모든 모델 클래스가 이걸 상속)
Base = declarative_base()

# DB 세션 의존성 함수 (요청마다 DB 세션 생성 -> 자동 닫힘)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
