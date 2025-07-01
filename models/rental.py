from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey
from database import Base

class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="대여 고유 관리 번호")
    student_id = Column(Integer, nullable=False, comment="대여자 학번")
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, comment="아이템 고유번호")
    rental_date = Column(DateTime, nullable=False, comment="대여일")
    expectation_return_date = Column(Date, nullable=False, comment="반납 예정일")
    return_date = Column(DateTime, nullable=True, comment="반납일")
    overdue = Column(Integer, default=0, comment="연체 여부 및 연체일 수")
    returned = Column(Boolean, default=False, nullable=False, comment="반납 여부")
    wish_student_id = Column(Integer, ForeignKey("users.student_id"), nullable=True, comment="희망 인원 학번")