from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import get_service, get_submission_service
from ..auth import get_current_user
from ..models.widget import Widget, WidgetCreate, WidgetUpdate
from ..services.widget_service import WidgetService
from ..services.submission_service import SubmissionService

router = APIRouter()


@router.post("/widgets", status_code=201, description="Create a new widget")
def create_widget(
    widget: WidgetCreate,
    owner_id: str = Depends(get_current_user),
    service: WidgetService = Depends(get_service),
):
    # call the service
    return service.create_widget(owner_id, widget)

@router.get("/widgets", description="List all widgets for the current owner")
def list_widgets(
    owner_id: str = Depends(get_current_user),
    service: WidgetService = Depends(get_service),
):
    return service.list_widgets(owner_id)

# get_widget
@router.get("/widgets/{widget_id}", description="Get one widget")
def get_widget(
    widget_id: str,
    owner_id: str = Depends(get_current_user),
    service: WidgetService = Depends(get_service),
):
    widget = service.get_widget(widget_id, owner_id)
    # if widget is None, raise HTTPException(404, ...); otherwise return it
    if widget is None:
        raise HTTPException(status_code=404, detail="widget not found")
    return widget

# update_widget
@router.put("/widgets/{widget_id}", description="Update an existing widget")
def update_widget(
    widget_id: str,
    widget: WidgetUpdate,
    owner_id: str = Depends(get_current_user),
    service: WidgetService = Depends(get_service),
):
    # call service, handle None -> 404, return result
    updated_widget = service.update_widget(widget_id, owner_id, widget)
    if updated_widget is None:
        raise HTTPException(status_code=404, detail="widget not found")
    return updated_widget

@router.delete("/widgets/{widget_id}", description="Delete a widget", status_code=204)
def delete_widget(
    widget_id: str,
    owner_id: str = Depends(get_current_user),
    service: WidgetService = Depends(get_service),
):
    # call service, handle False -> 404, return 204 No Content
    deleted = service.delete_widget(widget_id, owner_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Widget not found")
   
@router.get("/widgets/{widget_id}/embed", description="Get the embed snippet for a widget")
def get_embed_snippet(
    widget_id: str,
    owner_id: str = Depends(get_current_user),
    service: WidgetService = Depends(get_service),
):
    widget = service.get_widget(widget_id, owner_id)
    if widget is None:
        raise HTTPException(status_code=404, detail="Widget not found")
    return {"snippet": service.get_embed_snippet(widget_id)}


@router.get("/widgets/{widget_id}/submissions", description="List submissions for a widget (owner dashboard)")
def list_submissions(
    widget_id: str,
    owner_id: str = Depends(get_current_user),
    submission_service: SubmissionService = Depends(get_submission_service),
):
    return submission_service.list_submissions(widget_id, owner_id)

@router.get("/widgets/{widget_id}/stats", description="Basic stats for a widget's submissions")
def get_widget_stats(
    widget_id: str,
    owner_id: str = Depends(get_current_user),
    submission_service: SubmissionService = Depends(get_submission_service),
):
    submissions = submission_service.list_submissions(widget_id, owner_id)
    total = len(submissions)
    by_country = {}
    for s in submissions:
        country = s.country or "Unknown"
        by_country[country] = by_country.get(country, 0) + 1
    return {"total_submissions": total, "by_country": by_country}
