from ..repositories.widget_repository import WidgetRepository
from ..models.widget import Widget, WidgetCreate, WidgetUpdate
from typing import Optional


class WidgetService:
    """
    Business logic layer for widgets — sits between the HTTP routes and the
    database repository.

    Routes never call WidgetRepository directly; they always go through this
    service. Right now these methods are thin pass-throughs (call the
    repository, convert its plain dicts into Widget/Optional[Widget]/list[Widget]
    Pydantic objects), but this is deliberately where future business rules
    would go — e.g. "max N widgets per owner", "trim/normalize title text" —
    without routes or the repository needing to change.
    """
        
    def __init__(self, repository: WidgetRepository):
        self.repository = repository

    def create_widget(self, owner_id: str, widget: WidgetCreate) -> Widget:
        widget_dict = self.repository.create_widget(owner_id, widget)
        return Widget(**widget_dict)

    def get_widget(self, widget_id: str, owner_id: str) -> Optional[Widget]:
        widget_dict = self.repository.get_widget(widget_id, owner_id)
        # return Widget(**widget_dict) only if widget_dict exists, else None
        return Widget(**widget_dict) if widget_dict else None

    def list_widgets(self, owner_id: str) -> list[Widget]:
        widget_dicts = self.repository.list_widgets(owner_id)
        # convert each dict in the list into a Widget
        return [Widget(**widget_dict) for widget_dict in widget_dicts]

    def update_widget(self, widget_id: str, owner_id: str, widget: WidgetUpdate) -> Optional[Widget]:
        widget_dict = self.repository.update_widget(widget_id, owner_id, widget)
        # return Widget(**widget_dict) only if widget_dict exists, else None
        return Widget(**widget_dict) if widget_dict else None

    def delete_widget(self, widget_id: str, owner_id: str) -> bool:
        return self.repository.delete_widget(widget_id, owner_id)
