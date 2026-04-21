from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Court Feedback Kiosk Backend",
    version="0.1.0",
    root_path="/kiosk",
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Kiosk backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
