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


class AdminItemResponse(BaseModel) :
    success: bool
    code: int
    data: Optional[Item] = None

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


class AdminItemBase(BaseModel):
    item_id: int
    name: str
    type: ItemTypeEnum
    copy_status: CopyStatusEnum
    identifier_code: str
    hashtag: Optional[str]

    model_config = {
        "from_attributes": True,
        "exclude_none": True
    }

class AdminItemListResponse(BaseModel):
    success: bool
    code: int
    items: Optional[List[AdminItemBase]] = None
    page: Optional[int] = None
    size: Optional[int] = None

    model_config = {
        "exclude_none": True
    }