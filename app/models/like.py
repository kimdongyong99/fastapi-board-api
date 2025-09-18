from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.database import Base

class Like(Base):
    __tablename__ = "likes"

    like_id  = Column(Integer, primary_key=True, index=True)
    post_id  = Column(Integer, ForeignKey("posts.post_id", ondelete="CASCADE"), nullable=False, index=True)
    user_id  = Column(String(30), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")

    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_likes_post_user"),  # 한 유저가 같은 글에 1회만
        Index("ix_likes_post_created", "post_id", "created_at"),
    )
