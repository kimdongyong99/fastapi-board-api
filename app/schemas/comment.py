from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from pydantic import ConfigDict

class CommentBase(BaseModel):
    content: str = Field(..., min_length=1)

class CommentCreate(CommentBase):
    post_id: int

class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)

class CommentOut(CommentBase):
    comment_id: int
    post_id: int
    author_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)
