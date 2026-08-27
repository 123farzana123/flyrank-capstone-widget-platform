from fastapi import FastAPI
from .routes.widgets import router as widgets_router
from .routes.submissions import router as submissions_router
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .rate_limit import limiter
from fastapi.responses import FileResponse


app = FastAPI(
    title="Widget Platform API",
    description="Embeddable widget & lead-capture platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],  # the "customer website" test page's origin
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Serves the embed script as a plain static file at a fixed, predictable URL.
# Customer websites reference this directly via <script src="http://.../widget.js?id=...">,
# so the path must stay stable — this is the "versioned bundle" delivery point
@app.get("/widget.js")
def serve_widget_js():
    return FileResponse("app/static/widget.js", media_type="application/javascript")

app.include_router(widgets_router)
app.include_router(submissions_router)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/health", description="Check if the API is running")
def health_check():
    return {"status": "ok"}

