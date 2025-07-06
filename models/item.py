from sqlalchemy import Column, Integer, String, DateTime, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum
from database import Base
from dependencies import korea_time, DeletionStatusEnum

class ItemTypeEnum(str, Enum):
    BOOK = "book"         # 책
    EQUIPMENT = "equipment"   # 물품

class Item(Base):
    __tablename__ = "items"

    item_id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="아이템 고유 ID"
    )
    identifier_code = Column(
        String(100),
        unique=True,
        nullable=False,
        comment="ISBN 또는 고유 코드 (같은 책일 경우 동일한 코드 사용)"
    )
    name = Column(
        String(50),
        nullable=False,
        comment="아이템 이름 (최대 50자)"
    )
    type = Column(
        SQLEnum(ItemTypeEnum),
        nullable=False,
        default=ItemTypeEnum.BOOK,
        comment="아이템 종류 (book 또는 equipment)"
    )
    publisher = Column(
        String(50),
        comment="출판사 또는 제조사"
    )
    publish_date = Column(
        Date,
        comment="출판일 또는 출시일"
    )
    hashtag = Column(
        String(100),
        comment="해시태그 또는 키워드 검색용"
    )
    image_url = Column(
        String(100),
        comment="썸네일 이미지 URL"
    )
    total_count = Column(
        Integer,
        default=0,
        comment="등록된 복사본 총 수"
    )
    available_count = Column(
        Integer,
        default=0,
        comment="현재 대출 가능한 수량"
    )
    create_date = Column(
        DateTime,
        default=korea_time,
        comment="등록 시각"
    )
    update_date = Column(
        DateTime,
        default=korea_time,
        onupdate=korea_time,
        comment="수정 시각"
    )
    delete_status = Column(
        SQLEnum(DeletionStatusEnum),
        nullable=False,
        default=DeletionStatusEnum.ACTIVE,
        comment="삭제 상태 플래그"
    )

    copies = relationship("ItemCopy", back_populates="item")
