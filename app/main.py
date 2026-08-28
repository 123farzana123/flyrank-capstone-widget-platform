from fastapi import FastAPI, Request
from .routes.widgets import router as widgets_router
from .routes.submissions import router as submissions_router
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .rate_limit import limiter
from fastapi.responses import FileResponse, JSONResponse



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

MAX_BODY_SIZE = 100_000  # 100 KB — generous for a form submission, blocks abuse

@app.middleware("http")
async def limit_body_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_BODY_SIZE:
        return JSONResponse(status_code=413, content={"detail": "Payload too large"})
    return await call_next(request)

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

