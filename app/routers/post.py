# app/routers/post.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.database import get_db
from app.models.post import Post
from app.models.like import Like
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate, PostWithAuthorStatsOut
from app.schemas.like import LikeToggleOut
from app.core.security import get_current_user, get_current_user_optional

router = APIRouter()

# ------------------------------
# 게시글 생성
# ------------------------------
@router.post("", response_model=PostWithAuthorStatsOut, status_code=status.HTTP_201_CREATED)
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
    return PostWithAuthorStatsOut(
        post_id=post.post_id,
        title=post.title,
        content=post.content,
        author_id=post.author_id,
        created_at=post.created_at,
        updated_at=post.updated_at,
        author=post.author,
        likes_count=0,
        my_like=False
    )

# ------------------------------
# 게시글 목록 (작성자+좋아요 통계)
# ------------------------------
@router.get("", response_model=List[PostWithAuthorStatsOut])
def list_posts(q: Optional[str] = Query(None, description="제목/본문 키워드"),
               skip: int = Query(0, ge=0),
               limit: int = Query(20, ge=1, le=100),
               db: Session = Depends(get_db),
               current_user: Optional[User] = Depends(get_current_user_optional)):

    # 좋아요 수 서브쿼리
    likes_sq = (
        db.query(Like.post_id, func.count(Like.like_id).label("likes_count"))
          .group_by(Like.post_id)
          .subquery()
    )

    query = (
        db.query(Post, func.coalesce(likes_sq.c.likes_count, 0).label("likes_count"))
          .options(joinedload(Post.author))
          .outerjoin(likes_sq, Post.post_id == likes_sq.c.post_id)
          .order_by(Post.created_at.desc())
    )

    if q:
        query = query.filter((Post.title.contains(q)) | (Post.content.contains(q)))

    rows = query.offset(skip).limit(limit).all()

    # 내 좋아요 여부 조회
    my_liked_ids: set[int] = set()
    if current_user:
        liked_rows = db.query(Like.post_id).filter(Like.user_id == current_user.user_id).all()
        my_liked_ids = {r.post_id for r in liked_rows}

    result: List[PostWithAuthorStatsOut] = []
    for post, likes_count in rows:
        result.append(
            PostWithAuthorStatsOut(
                post_id=post.post_id,
                title=post.title,
                content=post.content,
                author_id=post.author_id,
                created_at=post.created_at,
                updated_at=post.updated_at,
                author=post.author,
                likes_count=int(likes_count),
                my_like=(post.post_id in my_liked_ids) if current_user else None,
            )
        )
    return result

# ------------------------------
# 게시글 상세
# ------------------------------
@router.get("/{post_id}", response_model=PostWithAuthorStatsOut)
def get_post(post_id: int,
             db: Session = Depends(get_db),
             current_user: Optional[User] = Depends(get_current_user_optional)):
    post = (
        db.query(Post)
          .options(joinedload(Post.author))
          .filter(Post.post_id == post_id)
          .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    likes_count = db.query(func.count(Like.like_id)).filter(Like.post_id == post_id).scalar() or 0
    my_like = None
    if current_user:
        my_like = db.query(Like).filter(
            Like.post_id == post_id, Like.user_id == current_user.user_id
        ).first() is not None

    return PostWithAuthorStatsOut(
        post_id=post.post_id,
        title=post.title,
        content=post.content,
        author_id=post.author_id,
        created_at=post.created_at,
        updated_at=post.updated_at,
        author=post.author,
        likes_count=int(likes_count),
        my_like=my_like,
    )

# ------------------------------
# 게시글 수정 (작성자 본인만)
# ------------------------------
@router.patch("/{post_id}", response_model=PostWithAuthorStatsOut)
def update_post(post_id: int, payload: PostUpdate,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You are not the author")

    if payload.title is not None:
        post.title = payload.title
    if payload.content is not None:
        post.content = payload.content

    db.commit()
    db.refresh(post)

    likes_count = db.query(func.count(Like.like_id)).filter(Like.post_id == post_id).scalar() or 0
    return PostWithAuthorStatsOut(
        post_id=post.post_id,
        title=post.title,
        content=post.content,
        author_id=post.author_id,
        created_at=post.created_at,
        updated_at=post.updated_at,
        author=post.author,
        likes_count=int(likes_count),
        my_like=False
    )

# ------------------------------
# 게시글 삭제 (작성자 본인만)
# ------------------------------
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You are not the author")

    db.delete(post)
    db.commit()
    return

# ------------------------------
# 좋아요 토글 (인증 필요)
# ------------------------------
@router.post("/{post_id}/like", response_model=LikeToggleOut)
def toggle_like(post_id: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    like = db.query(Like).filter(
        Like.post_id == post_id, Like.user_id == current_user.user_id
    ).first()

    if like:
        db.delete(like)
        db.commit()
        liked = False
    else:
        new_like = Like(post_id=post_id, user_id=current_user.user_id)
        db.add(new_like)
        db.commit()
        liked = True

    likes_count = db.query(func.count(Like.like_id)).filter(Like.post_id == post_id).scalar() or 0
    return LikeToggleOut(liked=liked, likes_count=int(likes_count))
