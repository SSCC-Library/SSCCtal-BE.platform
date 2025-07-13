from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from models.item import ItemTypeEnum
from models.item_copy import CopyStatusEnum

class ItemBase(BaseModel):
    name: str
    type: ItemTypeEnum
    identifier_code: str
    publisher: Optional[str] = None
    hashtag: Optional[str] = None
    image_url: Optional[str] = None
    total_count: Optional[int] = 0
    available_count: Optional[int] = 0



class ItemCreate(ItemBase):
    publish_date: Optional[date] = None
    
    model_config = {
        "from_attributes": True 
    }


class ItemResponse(ItemBase) :
    copy_status: Optional[CopyStatusEnum]=None

    model_config = {
        "from_attributes": True 
    }

class Item(ItemBase):
    item_id: int
    create_date: datetime
    update_date: datetime

    model_config = {
        "from_attributes": True,
        "exclude_none": True
    }



class ItemListResponse(BaseModel):
    success: bool
    code: int
    items: Optional[List[ItemBase]] = None
    page: Optional[int] = None
    size: Optional[int] = None

class ItemDetail(BaseModel):
    copy_id: int
    item_id: int
    identifier_code: str
    copy_status: CopyStatusEnum
    create_date: datetime
    update_date: datetime
    name: str
    type: ItemTypeEnum
    publisher: str
    publish_date: date
    hashtag: str
    image_url: str
    total_count: int
    available_count: int

    model_config = {
        "from_attributes": True,
        "use_enum_values": True
    }

class ItemCopyResponse(BaseModel):
    success: bool
    code: int
    item: Optional[ItemDetail] = None

    model_config = {
        "from_attributes": True
    }

class AdminItemSimple(BaseModel):
    copy_id: int
    item_id: int
    name: str
    type: str
    copy_status: CopyStatusEnum
    identifier_code: str
    hashtag: Optional[str]

    model_config = {
        "from_attributes": True,
        "use_enum_values": True  # enum → 문자열 변환
    }

class AdminItemListResponse(BaseModel):
    success: bool
    code: int
    items: Optional[List[AdminItemSimple]] = None
    total: Optional[int] = None
    page: Optional[int] = None
    size: Optional[int] = None