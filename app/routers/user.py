from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def users_health():
    return {"ok": True, "scope": "users"}
