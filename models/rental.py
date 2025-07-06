from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from enum import Enum
from dependencies import korea_time, DeletionStatusEnum

class RentalStatusEnum(str, Enum):
    BORROWED = "borrowed"     # 대여됨
    RETURNED = "returned"     # 반납됨
    OVERDUE = "overdue"       # 연체됨

class Rental(Base):
    __tablename__ = "rentals"

    rental_id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="대출 고유 ID (자동 증가)"
    )
    student_id = Column(
        Integer,
        ForeignKey("users.student_id"),
        nullable=False,
        comment="대출자 학번 (User 테이블 참조)"
    )
    copy_id = Column(
        Integer,
        ForeignKey("item_copies.copy_id"),  # ← 여기만 수정
        nullable=False,
        comment="대출한 복사본 ID (ItemCopy 테이블 참조)"
    )
    rental_status = Column(
        SQLEnum(RentalStatusEnum),
        nullable=False,
        default=RentalStatusEnum.BORROWED,
        comment="복사본의 대출 상태: borrowed(대여 중), returned(반납), overdue(연체)"
    )
    # rental_classification = Column(String)  # 대출 유형 구분 (예: short_term, reserved 등)

    item_borrow_date = Column(
        DateTime,
        comment="대출 일시"
    )
    expectation_return_date = Column(
        Date,
        comment="예상 반납일"
    )
    item_return_date = Column(
        DateTime,
        comment="실제 반납일 (반납 전이면 NULL)"
    )
    overdue = Column(
        Integer,
        default=0,
        comment="연체 일 수 또는 연체 여부 표시 (0이면 연체 아님)"
    )
    create_date = Column(
        DateTime,
        default=korea_time,
        comment="레코드 생성 시간"
    )
    update_date = Column(
        DateTime,
        default=korea_time,
        onupdate=korea_time,
        comment="레코드 수정 시간"
    )
    delete_status = Column(
        SQLEnum(DeletionStatusEnum),
        nullable=False,
        default=DeletionStatusEnum.ACTIVE,
        comment="삭제 상태 플래그"
    )

    user = relationship("User", back_populates="rentals")
    item_copy = relationship("ItemCopy", back_populates="rentals")
