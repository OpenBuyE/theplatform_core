import os
from dotenv import load_dotenv

load_dotenv()  # en local carga .env, en cloud usará env vars

class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change_me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ENV: str = os.getenv("ENV", "development")

    PROJECT_NAME: str = "The Platform Core API"
    VERSION: str = "1.0.0"

    # nombres de tablas esperadas en Supabase
    TABLE_USERS: str = "app_users_v2"
    TABLE_SESIONES: str = "sesiones_v2"
    TABLE_PARTICIPANTES: str = "participantes_v2"
    TABLE_PRODUCTOS: str = "productos_v2"
    TABLE_LOGS: str = "logs_v2"

settings = Settings()

