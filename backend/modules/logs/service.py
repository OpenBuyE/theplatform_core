from database.supabase_client import get_supabase
from core.config import settings


def list_logs(limit: int = 100) -> list[dict]:
    supabase = get_supabase()
    res = (
        supabase.table(settings.TABLE_LOGS)
        .select("*")
        .order("timestamp", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data or []
