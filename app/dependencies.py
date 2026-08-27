from .repositories.widget_repository import WidgetRepository
from .services.widget_service import WidgetService

_repository = WidgetRepository()
_service = WidgetService(_repository)

def get_service() -> WidgetService:
    return _service