from fastapi import APIRouter, Query

from .service import list_logs

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/")
def get_logs(limit: int = Query(100, ge=1, le=500)):
    return {"logs": list_logs(limit=limit)}
