from fastapi import FastAPI
from core.config import settings
from core.database import init_supabase

app = FastAPI(
    title="The Platform Core API",
    version="0.1.0",
    description="Núcleo de adjudicación y orquestación de CompraAbierta.com"
)

# Inicializar Supabase al arrancar
@app.on_event("startup")
def startup_event():
    try:
        init_supabase()
        print("Supabase inicializado correctamente.")
    except Exception as e:
        print(f"Error inicializando Supabase: {e}")


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "theplatform_core",
        "environment": settings.ENV,
        "supabase_connected": bool(settings.SUPABASE_URL),
        "version": "0.1.0"
    }
