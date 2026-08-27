from fastapi import APIRouter, Depends

from ..dependencies import get_submission_service
from ..models.submission import Submission, SubmissionCreate
from ..services.submission_service import SubmissionService

router = APIRouter()


@router.post("/widgets/{widget_id}/submissions", status_code=201, description="Submit a form (public, no auth)")
def create_submission(
    widget_id: str,
    submission: SubmissionCreate,
    service: SubmissionService = Depends(get_submission_service),
):
    # call service.create_submission(...)
    return service.create_submission(widget_id, submission.data)


