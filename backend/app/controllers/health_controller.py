from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
def check_health() -> dict[str, str]:
    return {"status": "ok"}
