from typing import Optional

from database.supabase_client import get_supabase
from core.config import settings
from core.security import hash_password, verify_password


def get_user_by_username(username: str) -> Optional[dict]:
    supabase = get_supabase()
    res = supabase.table(settings.TABLE_USERS).select("*").eq("username", username).limit(1).execute()
    data = res.data or []
    return data[0] if data else None


def create_user(username: str, password: str, role: str = "gestor", is_active: bool = True) -> dict:
    supabase = get_supabase()
    hashed = hash_password(password)
    res = supabase.table(settings.TABLE_USERS).insert(
        {
            "username": username,
            "password": hashed,
            "role": role,
            "is_active": is_active,
        }
    ).execute()
    return res.data[0] if res.data else {}


def validate_user(username: str, password: str) -> Optional[dict]:
    user = get_user_by_username(username)
    if not user:
        return None
    if not user.get("is_active", False):
        return None
    if not verify_password(password, user["password"]):
        return None
    return user

