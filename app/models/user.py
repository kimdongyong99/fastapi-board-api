from sqlalchemy import Column, String, DateTime, func, UniqueConstraint, Index
from app.database import Base
from sqlalchemy.orm import relationship
class User(Base):
    __tablename__ = "users"

    # 사용자 지정 아이디 (문자열 PK)
    user_id = Column(String(30), primary_key=True, nullable=False)

    username = Column(String(30), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")


    __table_args__ = (
        UniqueConstraint("username", name="uq_users_username"),
        UniqueConstraint("email", name="uq_users_email"),

    )

