from pydantic import BaseModel, Field
from typing import Optional

class Supplier(BaseModel):
    id: str = Field(..., description="Supplier identifier")
    name: str
    rating: Optional[float] = None
    active: bool = True
