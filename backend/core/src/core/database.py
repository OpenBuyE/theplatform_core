from supabase import create_client, Client
from .config import settings

supabase: Client = None

def init_supabase():
    global supabase

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("SUPABASE_URL o SUPABASE_KEY no configurados")

    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return supabase
