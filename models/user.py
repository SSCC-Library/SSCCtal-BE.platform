from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum
from database import Base
from dependencies import korea_time, DeletionStatusEnum

class UserClassificationEnum(str, Enum):
    STUDENT = "student"
    PROFESSOR = "professor"
    STAFF = "staff"
    GUEST = "guest"

class UserStatusEnum(str, Enum):
    ENROLLED = "enrolled"       # 재학생
    ON_LEAVE = "on_leave"       # 휴학생
    GRADUATED = "graduated"     # 졸업생
    DELETED = "deleted"         # 회원탈퇴

class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"

class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="내부용 PK (Auto Increment ID)"
    )
    student_id = Column(
        Integer,
        unique=True,
        nullable=False,
        comment="학번"
    )
    name = Column(
        String(10),
        nullable=False,
        comment="이름"
    )
    email = Column(
        String(30),
        nullable=False,
        unique=True,
        comment="이메일 주소"
    )
    phone_number = Column(
        String(150),
        comment="해시된 전화번호"
    )
    gender = Column(
        SQLEnum(GenderEnum),
        default=GenderEnum.MALE,
        comment='성별 ("male", "female")'
    )
    major = Column(
        String(10),
        nullable=False,
        comment="주전공"
    )
    major2 = Column(
        String(10),
        comment="복수전공 (선택)"
    )
    minor = Column(
        String(10),
        comment="부전공 (선택)"
    )
    user_classification = Column(
        SQLEnum(UserClassificationEnum),
        nullable=False,
        default=UserClassificationEnum.STUDENT,
        comment="사용자 분류 (학생, 교수 등)"
    )
    join_date = Column(
        DateTime,
        default=korea_time,
        comment="가입 일자 (기본값: 현재 시간)"
    )
    update_date = Column(
        DateTime,
        default=korea_time,
        onupdate=korea_time,
        comment="마지막 수정 시간"
    )
    user_status = Column(
        SQLEnum(UserStatusEnum),
        nullable=False,
        default=UserStatusEnum.ENROLLED,
        comment="사용자 상태 (재학생, 휴학생 등)"
    )
    delete_status = Column(
        SQLEnum(DeletionStatusEnum),
        nullable=False,
        default=DeletionStatusEnum.ACTIVE,
        comment="삭제 상태 플래그"
    )

    rentals = relationship("Rental", back_populates="user")
