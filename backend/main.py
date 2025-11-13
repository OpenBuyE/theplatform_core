from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from core.config import settings
from database.supabase_client import get_supabase
from modules.users.controller import router as auth_router
from modules.sessions.controller import router as sesiones_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Core API de The Platform (Compra Abierta SaaS) - Versión PRO",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # en producción, limitar
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "theplatform_core",
        "version": settings.VERSION,
        "time": datetime.utcnow().isoformat(),
    }

@app.get("/status")
def status():
    try:
        supabase = get_supabase()
        res = supabase.table(settings.TABLE_PRODUCTOS).select("id").execute()
        total_productos = len(res.data or [])
        return {
            "supabase": "conectado",
            "productos": total_productos,
            "env": settings.ENV,
            "time": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        return {"supabase": "error", "detalle": str(e)}

# Rutas de módulos
app.include_router(auth_router)
app.include_router(sesiones_router)

