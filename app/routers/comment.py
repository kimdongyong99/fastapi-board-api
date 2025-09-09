from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentOut
from app.core.security import get_current_user

router = APIRouter()  # 최종 prefix는 main에서 "/comments"

@router.get("/health")
def comments_health():
    return {"ok": True, "scope": "comments"}

# 생성 (인증 필요)
@router.post("", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(payload: CommentCreate,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.post_id == payload.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    c = Comment(
        post_id=payload.post_id,
        author_id=current_user.user_id,
        content=payload.content,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

# 목록 (공개) — 특정 게시글의 댓글
@router.get("", response_model=List[CommentOut])
def list_comments(post_id: int = Query(..., ge=1),  # ✅ 필수
                  skip: int = Query(0, ge=0),
                  limit: int = Query(20, ge=1, le=100),
                  db: Session = Depends(get_db)):
    q = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc())
    return q.offset(skip).limit(limit).all()

# 상세 (공개)
@router.get("/{comment_id}", response_model=CommentOut)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    c = db.query(Comment).filter(Comment.comment_id == comment_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    return c

# 수정 (작성자만)
@router.patch("/{comment_id}", response_model=CommentOut)
def update_comment(comment_id: int, payload: CommentUpdate,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    c = db.query(Comment).filter(Comment.comment_id == comment_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    if c.author_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You are not the author of this comment")

    if payload.content is not None:
        c.content = payload.content

    db.commit()
    db.refresh(c)
    return c

# 삭제 (작성자만)
@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    c = db.query(Comment).filter(Comment.comment_id == comment_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    if c.author_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You are not the author of this comment")

    db.delete(c)
    db.commit()
    return
