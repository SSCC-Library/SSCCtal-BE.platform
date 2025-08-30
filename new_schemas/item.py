from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from models.item import ItemTypeEnum
from models.item_copy import CopyStatusEnum
from dependencies import DeletionStatusEnum

class ItemBase(BaseModel):
    item_id: int
    identifier_code: str
    name: str
    type: ItemTypeEnum
    publisher: Optional[str]
    publish_date: Optional[date]
    hashtag: Optional[str]
    image_url: Optional[str]
    total_count: int
    available_count: int
    create_date: datetime
    update_date: datetime
    delete_status: DeletionStatusEnum

class ItemMainInfo(BaseModel) :
    name: str
    type: ItemTypeEnum
    hashtag: Optional[str] = None
    image_url: Optional[str] = None 
    
    model_config = {
        "from_attributes": True,
        "use_enum_values": True
    }

class AdminItemMainInfo(BaseModel) :
    item_id: int
    name: str
    type: ItemTypeEnum
    publisher: Optional[str]
    publish_date: Optional[date]
    hashtag: Optional[str]
    image_url: Optional[str]
    total_count: int
    available_count: int

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
