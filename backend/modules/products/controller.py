from fastapi import APIRouter, HTTPException

from .service import list_products, get_product

router = APIRouter(prefix="/productos", tags=["productos"])


@router.get("/")
def listar_productos():
    return {"productos": list_products()}


@router.get("/{producto_id}")
def obtener_producto(producto_id: str):
    prod = get_product(producto_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod
