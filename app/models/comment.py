from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base

class Comment(Base):
    __tablename__ = "comments"

    comment_id = Column(Integer, primary_key=True, index=True)
    post_id    = Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False, index=True)
    author_id  = Column(String(30), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    content    = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 관계
    author = relationship("User", back_populates="comments")
    post   = relationship("Post", back_populates="comments")

    __table_args__ = (
        Index("ix_comments_post_created", "post_id", "created_at"),
    )
