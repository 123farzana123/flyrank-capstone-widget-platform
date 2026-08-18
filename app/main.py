from fastapi import FastAPI

app = FastAPI(
    title="Widget Platform API",
    description="Embeddable widget & lead-capture platform",
    version="1.0.0",
)


@app.get("/health", description="Check if the API is running")
def health_check():
    return {"status": "ok"}