from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    student_id: int
    password: str

# 로그인 응답 스키마
class LoginResponse(BaseModel):
    success : bool
    code : int
    token: Optional[str] = None
    name: Optional[str] = None
    student_id : Optional[int] = None
    model_config = {
        "from_attributes": True,
        "exclude_none": True
    }