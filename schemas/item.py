from enum import Enum
from pydantic import BaseModel
from typing import Optional

class ItemTypeEnum(str, Enum):
    book = "book"
    daily_item = "daily_item"

class IsAvailableEnum(str, Enum):
    available = "available"
    rented = "rented"
    not_for_rent = "not_for_rent"
    lost = "lost"
    under_repair = "under_repair"

class ItemRead(BaseModel):
    id: int
    item_type: ItemTypeEnum
    name: str
    isbn: Optional[str] = None
    is_available: IsAvailableEnum
    hashtag: Optional[str] = None
    img: Optional[str] = None

    class Config:
        orm_mode = True

class ItemResponse(BaseModel):
    success: bool
    code: int
    item_id: Optional[int] = None
    title: Optional[str] = None
    status: Optional[IsAvailableEnum] = None
    img: Optional[str] = None
class ManualInputRequest(BaseModel):
    isbn: str