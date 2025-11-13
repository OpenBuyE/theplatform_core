# The Platform Core API (Backend v1.0)

Backend principal de la plataforma CompraAbierta / The Platform.

Tecnologías:
- FastAPI
- Supabase
- JWT (autenticación)
- Motor determinista de adjudicación

## Estructura

- `main.py`: punto de entrada FastAPI
- `core/`: configuración y seguridad
- `database/`: cliente Supabase
- `modules/`: módulos funcionales (usuarios, sesiones, productos, logs, adjudicación)

## Instalación local

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # y rellenar valores reales
uvicorn main:app --reload
