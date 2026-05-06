from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class UserOut(BaseModel):
    id: UUID
    phone: str
    created_at: datetime
    model_config={
        "from_attributes": True,
    }