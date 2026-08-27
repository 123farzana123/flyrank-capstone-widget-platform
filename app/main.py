from fastapi import FastAPI
from .routes.widgets import router as widgets_router
from .routes.submissions import router as submissions_router

app = FastAPI(
    title="Widget Platform API",
    description="Embeddable widget & lead-capture platform",
    version="1.0.0",
)


app.include_router(widgets_router)
app.include_router(submissions_router)

@app.get("/health", description="Check if the API is running")
def health_check():
    return {"status": "ok"}