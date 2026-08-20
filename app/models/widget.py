from pydantic import BaseModel
from typing import Literal, Optional 
from uuid import UUID
from datetime import datetime


class Widget(BaseModel):
    id: UUID
    owner_id: UUID
    widget_type: Literal["signup_form", "cta_popover"]
    title: str
    description: Optional[str] = None
    config: dict
    button_text: str
    created_at: datetime
    updated_at: datetime

class WidgetCreate(BaseModel):
    widget_type: Literal["signup_form", "cta_popover"]
    title: str
    description: Optional[str] = None
    config: dict
    button_text: str

class WidgetUpdate(BaseModel):
    title: str
    description: Optional[str] = None
    config: dict
    button_text: str