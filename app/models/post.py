# app/models/post.py
# 목적: 게시글 테이블 정의 + 작성자(User)와의 관계 설정

from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base

class Post(Base):
    __tablename__ = "posts"

    # 정수 PK (SQLite 오토 인크리먼트)
    post_id = Column(Integer, primary_key=True, index=True)

    # 제목/본문
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)

    # 작성자(FK) — User.user_id를 참조(문자열 PK)
    author_id = Column(String(30), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)

    # 생성/수정 시각
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # ORM 관계: Post.author ↔ User.posts
    author = relationship("User", back_populates="posts")

    __table_args__ = (
        Index("ix_posts_author_created", "author_id", "created_at"),
    )
