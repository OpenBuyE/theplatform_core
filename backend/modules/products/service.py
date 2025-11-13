from database.supabase_client import get_supabase
from core.config import settings


def list_products() -> list[dict]:
    supabase = get_supabase()
    res = supabase.table(settings.TABLE_PRODUCTOS).select("*").execute()
    return res.data or []


def get_product(producto_id: str) -> dict | None:
    supabase = get_supabase()
    res = supabase.table(settings.TABLE_PRODUCTOS).select("*").eq("id", producto_id).limit(1).execute()
    data = res.data or []
    return data[0] if data else None
