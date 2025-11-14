from pydantic import BaseModel, Field
from typing import List, Optional

class AdjudicationResult(BaseModel):
    purchase_id: str
    chosen_supplier_id: str
    score: float
    explanations: Optional[List[str]] = None
