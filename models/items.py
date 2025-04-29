from sqlalchemy import Column, String, Integer, Enum
from database import Base
import enum

class ItemType(str, enum.Enum):
    book = "book"
    daily_item = "daily_item"

class ItemAvailability(str, enum.Enum):
    available = "available"
    rented = "rented"
    not_for_rent = "not_for_rent"
    lost = "lost"
    under_repair = "under_repair"

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True, comment="SSCC 물품 고유 넘버")
    item_type = Column(Enum(ItemType), nullable=False, comment="물품 종류")
    name = Column(String(255),nullable=False, comment="물품 이름")
    isbn = Column(String(20), nullable=True, comment="책일 경우 ISBN")
    is_available = Column(Enum(ItemAvailability), nullable=False, comment="물품 상태")
    hashtag = Column(String(255), nullable=True, comment="물품 해시태그")
    img = Column(String(512), nullable=True, comment="물품 이미지 URL")
