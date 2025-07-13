from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.item_copy import CopyStatusEnum


class ItemCopyBase(BaseModel):
    item_id: int
    identifier_code: str
    copy_status: Optional[CopyStatusEnum] = CopyStatusEnum.AVAILABLE


class ItemCopyCreate(ItemCopyBase):
    pass

class ItemCopyUpdate(ItemCopyBase) :
    pass
class ItemCopyResponse(ItemCopyBase):
    copy_id: int
    create_date: datetime
    update_date: datetime

    model_config = {
        "from_attributes": True
    }