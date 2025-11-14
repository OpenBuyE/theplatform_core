from fastapi import FastAPI

app = FastAPI(
    title="The Platform Core API",
    version="0.1.0",
    description="Núcleo de adjudicación y orquestación de CompraAbierta.com"
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "theplatform_core", "version": "0.1.0"}
