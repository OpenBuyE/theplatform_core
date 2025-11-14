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
from fastapi import HTTPException
from adjudicator.models import AdjudicationInput
from adjudicator.engine import adjudicate_session

@app.post("/adjudicate")
def adjudicate(input_data: AdjudicationInput):
    try:
        result = adjudicate_session(input_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def health_check():
    return {
        "status": "ok",
        "service": "theplatform_core",
        "environment": settings.ENV,
        "supabase_connected": bool(settings.SUPABASE_URL),
        "version": "0.1.0"
    }
