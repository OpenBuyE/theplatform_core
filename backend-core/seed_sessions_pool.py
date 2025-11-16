"""
Seed script para poblar el PARQUE DE SESIONES (sessions_pool) de The Platform.

Usa productos de ejemplo:
- iPhone 15
- Samsung Galaxy S24
- MacBook Air M2
- PlayStation 5
- Nintendo Switch OLED

Crea:
- Cadenas por producto (XIPH15, XSAMS24, XMBAM2, XPS5, XNSWITCH)
- Sesiones programadas (scheduled) para el primer eslabón de cada cadena
- Sesiones en cadena (chain) para Xn.2, Xn.3, etc.
- Varias entradas standby para usar en el futuro

Requiere:
- Variables de entorno SUPABASE_URL y SUPABASE_KEY
- Que DatabaseService esté correctamente configurado
"""

from datetime import datetime, timedelta, timezone
from services.database import DatabaseService


db = DatabaseService()


PRODUCTS = [
    {
        "chain_group_id": "XIPH15",
        "product_id": "iphone_15",
        "name": "iPhone 15",
        "base_amount": 1199.0,
        "max_participants": 25,
    },
    {
        "chain_group_id": "XSAMS24",
        "product_id": "samsung_s24",
        "name": "Samsung Galaxy S24",
        "base_amount": 999.0,
        "max_participants": 25,
    },
    {
        "chain_group_id": "XMBAM2",
        "product_id": "macbook_air_m2",
        "name": "MacBook Air M2",
        "base_amount": 1499.0,
        "max_participants": 30,
    },
    {
        "chain_group_id": "XPS5",
        "product_id": "ps5",
        "name": "PlayStation 5",
        "base_amount": 599.0,
        "max_participants": 20,
    },
    {
        "chain_group_id": "XNSWITCH",
        "product_id": "switch_oled",
        "name": "Nintendo Switch OLED",
        "base_amount": 399.0,
        "max_participants": 20,
    },
]


OPERATORS = ["ES", "PT", "FR"]  # Operadores de ejemplo


def create_chain_entries_for_product(product: dict, operator_code: str, chain_length: int = 5):
    """
    Crea en sessions_pool la cadena de sesiones para un producto y operador:
    - 1 entrada 'scheduled' (primer eslabón) con start_timestamp = ahora + offset
    - (chain_length - 1) entradas 'chain' para los siguientes eslabones
    """

    now_utc = datetime.now(timezone.utc)

    chain_group_id = product["chain_group_id"]
    product_id = product["product_id"]
    amount = product["base_amount"]
    max_participants = product["max_participants"]

    # 1) Primera sesión de la cadena: 'scheduled'
    #    Se activará automáticamente cuando start_timestamp <= now (según worker)
    start_ts = now_utc + timedelta(minutes=1)  # ejemplo: dentro de 1 minuto

    first_data = {
        "product_id": product_id,
        "operator_code": operator_code,
        "type": "scheduled",
        "chain_group_id": chain_group_id,
        "chain_index": 1,
        "max_participants": max_participants,
        "amount": amount,
        "start_timestamp": start_ts.isoformat(),
        "description": f"{product['name']} - Cadena {chain_group_id} - Sesión 1 ({operator_code})",
    }

    res_first = db.insert("sessions_pool", first_data)
    print(f"[OK] Primera sesión programada en cadena {chain_group_id} para operador {operator_code}: {res_first.data[0]['id']}")

    # 2) Resto de sesiones de la cadena: type = 'chain'
    #    No tienen start_timestamp, se usarán como plantillas Xn.2, Xn.3, etc.
    for idx in range(2, chain_length + 1):
        data = {
            "product_id": product_id,
            "operator_code": operator_code,
            "type": "chain",
            "chain_group_id": chain_group_id,
            "chain_index": idx,
            "max_participants": max_participants,
            "amount": amount,
            "start_timestamp": None,
            "description": f"{product['name']} - Cadena {chain_group_id} - Sesión {idx} ({operator_code})",
        }
        res = db.insert("sessions_pool", data)
        print(f"[OK] Sesión cadena {chain_group_id}.{idx} para operador {operator_code}: {res.data[0]['id']}")


def create_standby_entries(product: dict, operator_code: str, count: int = 3):
    """
    Crea algunas entradas 'standby' sin cadena ni fecha de inicio.
    Estas sirven como sesiones futuras que el operador puede activar cuando quiera.
    """

    amount = product["base_amount"]
    max_participants = product["max_participants"]

    for i in range(1, count + 1):
        data = {
            "product_id": product["product_id"],
            "operator_code": operator_code,
            "type": "standby",
            "chain_group_id": None,
            "chain_index": None,
            "max_participants": max_participants,
            "amount": amount,
            "start_timestamp": None,
            "description": f"{product['name']} - Standby #{i} ({operator_code})",
        }
        res = db.insert("sessions_pool", data)
        print(f"[OK] Sesión standby creada para {product['name']} ({operator_code}): {res.data[0]['id']}")


def seed_sessions_pool():
    print("=== Iniciando seed de sessions_pool ===")
    for product in PRODUCTS:
        for op in OPERATORS:
            # Cadenas automáticas por producto y operador
            create_chain_entries_for_product(product, op, chain_length=5)

            # Algunas sesiones standby adicionales
            create_standby_entries(product, op, count=2)

    print("=== Seed de sessions_pool completado ===")


if __name__ == "__main__":
    seed_sessions_pool()
