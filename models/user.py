from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from enum import Enum
from database import Base
from dependencies import korea_time, DeletionStatusEnum

class UserClassificationEnum(str, Enum):
    STUDENT = "student"
    PROFESSOR = "professor"
    STAFF = "staff"
    GUEST = "guest"

class UserStatusEnum(str, Enum):
    ENROLLED = "enrolled"   #재학생
    ON_LEAVE = "on_leave"   #휴학생
    GRADUATED = "graduated" #졸업생
    DELETED = "deleted" #회원탈퇴


class User(Base):
    __tablename__ = "users"  # 이 모델이 매핑될 테이블 이름

    id = Column(Integer, primary_key=True, index=True)  # 내부용 PK (Auto Increment ID)
    student_id = Column(Integer, unique=True, nullable=False)  # 학번
    name = Column(String(10), nullable=False)  # 이름
    email = Column(String(30), nullable=False, unique=True)  # 이메일 주소
    phone_number = Column(String(150))  # 해시된 전화번호
    gender = Column(String(10))  # 성별 (예: "male", "female")
    major = Column(String(10),nullable=False)  # 주전공
    major2 = Column(String(10))  # 복수전공 (선택)
    minor = Column(String(10))  # 부전공 (선택)
    user_classification = Column(SQLEnum(UserClassificationEnum), nullable=False,default=UserClassificationEnum.STUDENT)  # 사용자 분류 (학생, 교수 등)
    joined_at = Column(DateTime, default=korea_time)  # 가입 일자 (기본값: 현재 시간)
    updated_at = Column(DateTime, default=korea_time, onupdate=korea_time)  # 마지막 수정 시간
    user_status = Column(SQLEnum(UserStatusEnum), nullable=False, default=UserStatusEnum.ENROLLED)
    delete_status = Column(SQLEnum(DeletionStatusEnum),nullable=False, default=DeletionStatusEnum.ACTIVE)
    # 사용자 상태 (재학생, 휴학생 등)

    rentals = relationship("Rental", back_populates="user")  # 대출 이력과의 관계 (1:N)
