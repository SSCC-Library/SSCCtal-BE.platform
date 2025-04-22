"""
Pydantic 요청/응답 스키마 정의
"""
from pydantic import BaseModel

# 클라이언트가 학번으로 사용자 조회 요청 시 사용하는 요청 스키마
class SchoolNumberRequest(BaseModel):
    student_id: int

# 사용자 정보를 응답할 때 사용하는 응답 스키마
class UserResponse(BaseModel):
    id: int
    student_id: int
    email: str
    name: str
    major: str

    class Config:
        orm_mode = True    # SQLAlchemy 모델과 호환되도록 설정
