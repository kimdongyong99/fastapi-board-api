from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, TokenOut
from app.core.security import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/health")
def users_health():
    return {"ok": True, "scope": "users"}

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(data: UserCreate, db: Session = Depends(get_db)):
    # user_id / username / email 중복 체크
    if db.query(User).filter(
        (User.user_id == data.user_id) | (User.username == data.username) | (User.email == data.email)
    ).first():
        raise HTTPException(status_code=400, detail="user_id or username or email already exists")

    user = User(
        user_id=data.user_id,
        username=data.username,
        email=data.email,
        password=get_password_hash(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(User).filter(User.username == form.username).first()
    if not user:
        user = db.query(User).filter(User.user_id == form.username).first()

    if not user or not verify_password(form.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.user_id)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
