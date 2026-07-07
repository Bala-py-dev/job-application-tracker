from sqlalchemy.orm import Session

from app.logger import get_logger
from app.models import Application, StatusEvent
from app.schemas import ApplicationCreate, ApplicationUpdate

logger = get_logger(__name__)


def create_application(db: Session, data: ApplicationCreate) -> Application:
    application = Application(**data.model_dump())
    db.add(application)
    db.flush()

    event = StatusEvent(
        application_id=application.id,
        old_status=None,
        new_status=application.status,
        note="Application created",
    )
    db.add(event)

    db.commit()
    db.refresh(application)
    logger.info("Created application %s for %s", application.id, application.company)
    return application


def list_applications(db: Session, status: str | None = None) -> list[Application]:
    query = db.query(Application)
    if status:
        query = query.filter(Application.status == status)
    return query.order_by(Application.created_at.desc()).all()


def get_application(db: Session, application_id: int) -> Application | None:
    return db.query(Application).filter(Application.id == application_id).first()


def update_application(
    db: Session, application: Application, data: ApplicationUpdate
) -> Application:
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)
    logger.info("Updated application %s", application.id)
    return application


def change_status(
    db: Session, application: Application, new_status, note: str | None
) -> Application:
    old_status = application.status
    application.status = new_status

    event = StatusEvent(
        application_id=application.id,
        old_status=old_status,
        new_status=new_status,
        note=note,
    )
    db.add(event)

    db.commit()
    db.refresh(application)
    logger.info(
        "Application %s status changed from %s to %s",
        application.id,
        old_status,
        new_status,
    )
    return application


def delete_application(db: Session, application: Application) -> None:
    db.delete(application)
    db.commit()
    logger.info("Deleted application %s", application.id)
