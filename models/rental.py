from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey,Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from database import Base
from enum import Enum
from dependencies import korea_time, DeletionStatusEnum

class RentalStatusEnum(str, Enum):
    BORROWED = "borrowed"     # 대여됨
    RETURNED = "returned"     # 반납됨
    OVERDUE = "overdue"       # 연체됨


class Rental(Base):
    __tablename__ = "rentals"  # 이 모델이 매핑될 테이블 이름

    rental_id = Column(Integer, primary_key=True, index=True)  # 대출 고유 ID (자동 증가)
    student_id = Column(Integer, ForeignKey("users.student_id"), nullable=False)  # 대출자 학번 (User 테이블 참조)
    copy_id = Column(Integer, ForeignKey("item_copy.copy_id"), nullable=False)  # 대출한 복사본 ID (ItemCopy 참조)

    copy_status = Column(SQLEnum(RentalStatusEnum), nullable=False, default=RentalStatusEnum.BORROWED)
    # 복사본의 대출 상태: borrowed(대여 중), returned(반납), overdue(연체)

    # rental_classification = Column(String) # 대출 유형 구분 (예: short_term, reserved 등) → 현재 주석 처리됨

    item_borrow_date = Column(DateTime)  # 대출 일시
    expectation_return_date = Column(Date)  # 예상 반납일
    item_return_date = Column(DateTime)  # 실제 반납일 (반납 전이면 null)

    overdue = Column(Integer, default=0)  # 연체 일 수 또는 연체 여부 표시 (0이면 연체 아님)

    created_at = Column(DateTime, default=korea_time)  # 레코드 생성 시간
    updated_at = Column(DateTime, default=korea_time, onupdate=korea_time)  # 레코드 수정 시간
    delete_status = Column(SQLEnum(DeletionStatusEnum),nullable=False, default=DeletionStatusEnum.ACTIVE)

    user = relationship("User", back_populates="rentals")  # 사용자와의 관계 (1:N)
    item_copy = relationship("ItemCopy", back_populates="rentals")  # 복사본과의 관계 (1:N)

