from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timedelta
from enum import Enum
from database import Base
from dependencies import korea_time, DeletionStatusEnum

class Item_typeEnum(str, Enum) :
    BOOK = "book"   #책
    ITEM = "item"   #물품


class Item(Base):
    __tablename__ = "items"  # 아이템(책, 장비 등) 테이블

    item_id = Column(Integer, primary_key=True, index=True)  # 아이템 ID
    item_isbn = Column(String(100), unique=True,nullable=False)  # ISBN 또는 고유 코드(같은 책일 시 같은 isbn)
    name = Column(String(20), nullable=False)  # 아이템 이름 (최대 20자)
    type = Column(SQLEnum(Item_typeEnum), nullable=False,default=Item_typeEnum.BOOK)  # 아이템 종류 (예: book, item 등 Enum)
    publisher = Column(String(20))  # 출판사 (또는 제조사)
    publish_date = Column(Date)  # 출판일 또는 출시일
    hashtag = Column(String(100))  # 해시태그 또는 키워드 검색용
    image_url = Column(String(100))  # 썸네일 이미지 URL
    total_count = Column(Integer, default=0)  # 등록된 복사본 총 수
    available_count = Column(Integer, default=0)  # 현재 대출 가능한 수량
    created_at = Column(DateTime, default=korea_time)  # 등록 시각
    updated_at = Column(DateTime, default=korea_time, onupdate=korea_time)  # 수정 시각
    delete_status = Column(SQLEnum(DeletionStatusEnum),nullable=False, default=DeletionStatusEnum.ACTIVE)

    copies = relationship("ItemCopy", back_populates="item")  # 복사본들과의 관계 (1:N)


class Copy_StatusEnum(str, Enum):
    AVAILABLE = "available"         # 대출 가능
    BORROWED = "borrowed"           # 대여 중
    LOST = "lost"                   # 분실
    DAMAGED = "damaged"             # 손상됨
    UNDER_REPAIR = "under_repair"   # 수리 중


class ItemCopy(Base):
    __tablename__ = "item_copy"  # 복사본 테이블 (실물 단위)

    copy_id = Column(Integer, primary_key=True, index=True)  # 복사본 고유 ID
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=False)  # 연결된 아이템의 ID
    identifier_code = Column(String(100), nullable=False, unique=True)  # 실물 식별 코드 (예: 바코드, RFID)
    copy_status = Column(SQLEnum(Copy_StatusEnum), nullable=False, default=Copy_StatusEnum.AVAILABLE)
    # 복사본의 상태 (대출 가능, 분실 등)

    created_at = Column(DateTime, default=korea_time)  # 생성 시각
    updated_at = Column(DateTime, default=korea_time, onupdate=korea_time)  # 수정 시각
    delete_status = Column(SQLEnum(DeletionStatusEnum),nullable=False, default=DeletionStatusEnum.ACTIVE)

    item = relationship("Item", back_populates="copies")  # 원본 아이템과의 관계
    rentals = relationship("Rental", back_populates="item_copy")  # 대출 기록과의 관계