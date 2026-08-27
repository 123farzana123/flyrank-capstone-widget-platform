from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class SubmissionCreate(BaseModel):
    data: dict


class Submission(BaseModel):
    # id, widget_id, data, ip_address, country, city, created_at
    id: int
    widget_id: UUID
    data: dict
    ip_address: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    created_at: datetime