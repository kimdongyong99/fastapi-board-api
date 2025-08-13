from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def posts_health():
    return {"ok": True, "scope": "posts"}
