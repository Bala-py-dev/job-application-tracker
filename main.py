from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import init_db
from app.logger import get_logger
from app.routers import applications, reminders

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("%s started", settings.app_name)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(applications.router)
app.include_router(reminders.router)


@app.get("/")
def root():
    return {"app": settings.app_name, "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}
