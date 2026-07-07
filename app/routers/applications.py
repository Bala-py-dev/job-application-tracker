from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ApplicationStatus
from app.schemas import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationUpdate,
    EmailIn,
    ExtractedApplication,
    StatusUpdate,
)
from app.services import application_service
from app.services.ai_extractor import extract_from_email

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create(data: ApplicationCreate, db: Session = Depends(get_db)):
    return application_service.create_application(db, data)


@router.get("", response_model=list[ApplicationOut])
def list_all(
    status: ApplicationStatus | None = None, db: Session = Depends(get_db)
):
    return application_service.list_applications(db, status)


@router.get("/{application_id}", response_model=ApplicationOut)
def get_one(application_id: int, db: Session = Depends(get_db)):
    application = application_service.get_application(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.patch("/{application_id}", response_model=ApplicationOut)
def update(
    application_id: int, data: ApplicationUpdate, db: Session = Depends(get_db)
):
    application = application_service.get_application(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application_service.update_application(db, application, data)


@router.post("/{application_id}/status", response_model=ApplicationOut)
def change_status(
    application_id: int, data: StatusUpdate, db: Session = Depends(get_db)
):
    application = application_service.get_application(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application_service.change_status(db, application, data.status, data.note)


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(application_id: int, db: Session = Depends(get_db)):
    application = application_service.get_application(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    application_service.delete_application(db, application)


@router.post("/extract", response_model=ExtractedApplication)
def extract(data: EmailIn):
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Email text cannot be empty")
    return extract_from_email(data.text)
