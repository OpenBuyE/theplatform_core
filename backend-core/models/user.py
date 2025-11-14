from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class User(BaseModel):
    id: str = Field(..., description="Unique user identifier")
    email: EmailStr
    full_name: Optional[str] = None
    created_at: Optional[str] = None
