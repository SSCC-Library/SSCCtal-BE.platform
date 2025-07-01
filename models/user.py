"""
SQLAlchemy 모델 정의
"""
from sqlalchemy import Column, Integer, String
from database import Base

# users 테이블에 해당하는 SQLAlchemy ORM 모델 정의
class User(Base):
    __tablename__ = "users"    # 테이블 이름 지정

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)    # 기본 키
    student_id = Column(Integer, unique=True, index=True, nullable=False)    # 학번(고유)
    email = Column(String(255), unique=True, nullable=False)    # 이메일 (고유)
    name = Column(String(255), nullable=False)    # 이름
    major = Column(String(255), nullable=False)    # 전공