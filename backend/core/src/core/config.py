import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    ENV: str = os.getenv("ENV", "development")

    # Supabase / PostgreSQL
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # JWT tokens (para operadores, panel interno, etc.)
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change_me_please")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24  # 24h

    class Config:
        env_file = ".env"

settings = Settings()
