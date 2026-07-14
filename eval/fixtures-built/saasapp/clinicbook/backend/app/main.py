"""clinicbook API entrypoint."""
from fastapi import FastAPI

from backend.app.exports import router as exports_router
from backend.app.routers.patients import router as patients_router

app = FastAPI(title="clinicbook")
app.include_router(patients_router)
app.include_router(exports_router)
