from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from models.item import ItemTypeEnum

class ItemBase(BaseModel):
    identifier_code: str
    name: str
    type: ItemTypeEnum
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
    create_date: datetime
    update_date: datetime

    model_config = {
        "from_attributes": True
    }

