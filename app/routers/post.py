# app/routers/post.py
# 목적: 게시글 CRUD + 권한(작성자만 수정/삭제)
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostOut
from app.core.security import get_current_user

router = APIRouter()  # 최종 prefix는 main에서 "/posts"

@router.get("/health")
def posts_health():
    return {"ok": True, "scope": "posts"}

# 1) 생성: 인증 필요 (현재 사용자 = 작성자)
@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(payload: PostCreate,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    post = Post(
        title=payload.title,
        content=payload.content,
        author_id=current_user.user_id,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

# 2) 목록: 공개 (검색/페이지네이션)
@router.get("", response_model=List[PostOut])
def list_posts(q: Optional[str] = Query(None, description="제목/본문 키워드 검색"),
               skip: int = Query(0, ge=0),
               limit: int = Query(20, ge=1, le=100),
               db: Session = Depends(get_db)):
    query = db.query(Post).order_by(Post.created_at.desc())
    if q:
        # 간단한 부분검색 (SQLite는 대소문자 약하게 구분)
        query = query.filter((Post.title.contains(q)) | (Post.content.contains(q)))
    posts = query.offset(skip).limit(limit).all()
    return posts

# 3) 상세: 공개
@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# 4) 부분수정: 작성자만
@router.patch("/{post_id}", response_model=PostOut)
def update_post(post_id: int, payload: PostUpdate,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You are not the author of this post")

    # 부분 업데이트(넘어온 값만)
    if payload.title is not None:
        post.title = payload.title
    if payload.content is not None:
        post.content = payload.content

    db.commit()
    db.refresh(post)
    return post

# 5) 삭제: 작성자만
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You are not the author of this post")

    db.delete(post)
    db.commit()
    return  # 204 No Content
