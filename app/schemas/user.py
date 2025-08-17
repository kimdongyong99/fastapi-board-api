from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict

# 공통 베이스 (응답·요청 공통 필드)
class UserBase(BaseModel):
    user_id: str = Field(..., min_length=3, max_length=30)   # 문자열 PK
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr

# 회원가입 요청
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

# 응답(비밀번호 제외)
class UserOut(UserBase):
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)

# 토큰 응답
class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
