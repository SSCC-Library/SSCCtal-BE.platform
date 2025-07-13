from pydantic import BaseModel, GenericModel
from typing import TypeVar, Generic, Optional


T = TypeVar("T")

class CommonResponse(GenericModel, Generic[T]):
    success: bool
    code: int
    data: Optional[T] = None

    model_config = {
        "from_attributes": True,
        "use_enum_values": True
    }