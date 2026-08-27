from fastapi import APIRouter, Depends, Request, Response as FastAPIResponse

from ..dependencies import get_submission_service, get_service
from ..models.submission import Submission, SubmissionCreate
from ..services.submission_service import SubmissionService
from ..rate_limit import limiter
from ..geo import get_geo_from_ip
from ..email import send_confirmation_email

router = APIRouter()


@router.post("/widgets/{widget_id}/submissions", status_code=201, description="Submit a form (public, no auth)")
@limiter.limit("5/minute")
def create_submission(
    request: Request,  # slowapi requires this parameter to inspect the incoming request
    widget_id: str,
    submission: SubmissionCreate,
    response: FastAPIResponse,
    service: SubmissionService = Depends(get_submission_service),
):
    _ = request  # keep the request parameter for slowapi rate limiting checks

    if submission.website:  # honeypot filled in -> bot
        response.status_code = 204
        return
    
    visitor_ip = request.client.host
    geo = get_geo_from_ip(visitor_ip)

    result = service.create_submission(
        widget_id, submission.data,
        ip_address=visitor_ip, country=geo["country"], city=geo["city"],
    )

    try:
        send_confirmation_email(submission.data)
    except Exception:
        pass  # non-critical failure — submission already succeeded, don't break the response

    return result


@router.get("/widgets/{widget_id}/config", description="Get widget config for rendering (public, cached)")
def get_widget_config(widget_id: str, response: FastAPIResponse, service=Depends(get_service)):
    widget = service.get_widget_public(widget_id)
    if widget is None:
        response.status_code = 404
        return {"detail": "Widget not found"}

    response.headers["Cache-Control"] = "public, max-age=60"  # short-lived cache, per brief §4.3
    return {
        "widget_type": widget.widget_type,
        "title": widget.title,
        "description": widget.description,
        "config": widget.config,
        "button_text": widget.button_text,
    }

