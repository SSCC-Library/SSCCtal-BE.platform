from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum
from database import Base
from dependencies import korea_time, DeletionStatusEnum


class CopyStatusEnum(str, Enum):
    AVAILABLE = "available"         # 대출 가능
    BORROWED = "borrowed"           # 대여 중
    LOST = "lost"                   # 분실
    DAMAGED = "damaged"             # 손상됨
    UNDER_REPAIR = "under_repair"   # 수리 중


class ItemCopy(Base):
    __tablename__ = "item_copies"

    copy_id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="복사본 고유 ID"
    )
    item_id = Column(
        Integer,
        ForeignKey("items.item_id"),
        nullable=False,
        comment="연결된 아이템의 ID"
    )
    identifier_code = Column(
        String(100),
        nullable=False,
        unique=True,
        comment="실물 식별 코드 (예: 바코드, RFID)"
    )
    copy_status = Column(
        SQLEnum(CopyStatusEnum),
        nullable=False,
        default=CopyStatusEnum.AVAILABLE,
        comment="복사본 상태 (대출 가능, 대여 중, 분실 등)"
    )
    create_date = Column(DateTime,
        default=korea_time,
        comment="생성 시각"
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

    item = relationship("Item", back_populates="copies")
    rentals = relationship("Rental", back_populates="item_copy")
