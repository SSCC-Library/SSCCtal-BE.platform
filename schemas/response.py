from pydantic import BaseModel
from typing import TypeVar, Generic, Optional
from new_schemas.user import UserSimpleInfo
from new_schemas.rental import RentalMainInfo

T = TypeVar("T")

class CommonResponse(BaseModel, Generic[T]):
    success: bool
    code: int
    data: Optional[T] = None

    model_config = {
        "from_attributes": True,
        "use_enum_values": True
    }

class RentalWithUserData(BaseModel):
    user: UserSimpleInfo
    rental: RentalMainInfo