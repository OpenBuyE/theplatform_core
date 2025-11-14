from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Purchase(BaseModel):
    id: str = Field(..., description="Unique identifier for the purchase")
    user_id: str = Field(..., description="User who initiated the purchase")
    amount: float = Field(..., gt=0, description="Amount of the purchase")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending", description="Purchase status")
