from pydantic import BaseModel
from typing import TypeVar, Generic, Optional
from new_schemas.user import UserSimpleInfo
from new_schemas.rental import RentalMainInfo,OverdueResponse
from new_schemas.item import AdminItemMainInfo,ItemMainInfo
from new_schemas.item_copy import ItemCopyBase,ItemCopyMainInfo

T = TypeVar("T")

class CommonResponse(BaseModel, Generic[T]):
    success: bool
    code: int
    data: Optional[T] = None

    model_config = {
        "from_attributes": True,
        "use_enum_values": True
    }
    total:Optional[int]=None
    page: Optional[int] = None
    size: Optional[int] = None

class RentalWithUserData(BaseModel):
    user: UserSimpleInfo
    rental: RentalMainInfo

class ItemWithItemCopyData(BaseModel) :
    item_copy : ItemCopyBase
    item : AdminItemMainInfo

class ListItemWithCopyData(BaseModel) :
    item_copy: ItemCopyMainInfo
    item: AdminItemMainInfo