# app/schemas/post.py
# 목적: 게시글 API의 요청/응답 구조 정의
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from pydantic import ConfigDict

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)

class PostCreate(PostBase):
    """게시글 생성 요청 바디"""

class PostUpdate(BaseModel):
    """게시글 부분 수정(둘 중 하나 이상 포함)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)

class PostOut(PostBase):
    post_id: int
    author_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # SQLAlchemy 모델에서 바로 직렬화되도록
    model_config = ConfigDict(from_attributes=True)
