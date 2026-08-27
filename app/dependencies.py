from .repositories.widget_repository import WidgetRepository
from .services.widget_service import WidgetService
from .services.submission_service import SubmissionService
from .repositories.submission_repository import SubmissionRepository

_repository = WidgetRepository()
_service = WidgetService(_repository)
_submission_repository = SubmissionRepository()
_submission_service = SubmissionService(_submission_repository)

def get_service() -> WidgetService:
    return _service

def get_submission_service() -> SubmissionService:
    return _submission_service