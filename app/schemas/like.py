from pydantic import BaseModel

class LikeToggleOut(BaseModel):
    liked: bool        # 이번 요청 결과: 좋아요 상태
    likes_count: int   # 현재 총 좋아요 수
