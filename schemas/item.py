from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from models.item import Item_typeEnum, Copy_StatusEnum
from dependencies import DeletionStatusEnum

class ItemBase(BaseModel):
    item_isbn: str
    name: str
    type: Item_typeEnum
    publisher: Optional[str] = None
    publish_date: Optional[date] = None
    hashtag: Optional[str] = None
    image_url: Optional[str] = None
    total_count: Optional[int] = 0
    available_count: Optional[int] = 0


class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    item_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }



class ItemCopyBase(BaseModel):
    item_id: int
    identifier_code: str
    copy_status: Optional[Copy_StatusEnum] = Copy_StatusEnum.AVAILABLE


class ItemCopyCreate(ItemCopyBase):
    pass

class ItemCopyUpdate(ItemCopyBase) :
    pass
class ItemCopySchemas(ItemCopyBase):
    copy_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }