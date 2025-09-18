from fastapi import FastAPI
from app.database import Base, engine
from app.routers import user, post
from app.core.config import settings
from app.models import user as user_model
from app.models import post as post_model
from app.routers import comment as comment_router
from app.models import comment as comment_model
from app.models import like as like_model
app = FastAPI(title=settings.PROJECT_NAME)

# 추후 모델 추가 시 자동 생성
Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(post.router, prefix="/posts", tags=["Posts"])
app.include_router(comment_router.router, prefix="/comments", tags=["Comments"])
@app.get("/")
def root():
    return {"message": "Welcome to FastAPI Board API"}
