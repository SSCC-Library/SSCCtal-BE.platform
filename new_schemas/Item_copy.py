from pydantic import BaseModel
from datetime import datetime
from models.item_copy import CopyStatusEnum
from dependencies import DeletionStatusEnum

class ItemCopyBase(BaseModel):
    copy_id: int
    item_id: int
    identifier_code: str
    copy_status: CopyStatusEnum
    create_date: datetime
    update_date: datetime
    delete_status: DeletionStatusEnum

    model_config = {
        "from_attributes": True
    }

class ItemCopyMainInfo(BaseModel) :
    copy_id: int
    item_id: int
    identifier_code: str
    copy_status: CopyStatusEnum

    model_config = {
        "from_attributes": True,
        "use_enum_values": True
    }