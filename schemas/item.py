from enum import Enum
from pydantic import BaseModel

class ItemAvailability(str, Enum):
    available = "available"
    rented = "rented"
    not_for_rent = "not_for_rent"
    lost = "lost"
    under_repair = "under_repair"

class ManualInputRequest(BaseModel):
    isbn: str

class ItemResponse(BaseModel):
    success: bool
    code: int
    item_id: int = None
    title: str = None
    status: ItemAvailability = None
    img: str = None
