from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.item_copy import CopyStatusEnum
from dependencies import DeletionStatusEnum

class ItemCopyBase(BaseModel):
    copy_id: int
    item_id: int
    identifier_code: str
    copy_status: CopyStatusEnum
    created_at: datetime
    updated_at: datetime
    delete_status: DeletionStatusEnum

class ItemMainInfo(BaseModel) :
    copy_id: int
    item_id: int
    identifier_code: str
    copy_status: CopyStatusEnum