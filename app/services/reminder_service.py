from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models import TERMINAL_STATUSES, Application
from app.utils import utcnow


def get_due_reminders(db: Session, until: datetime | None = None) -> list[Application]:
    deadline = until or utcnow()
    terminal_values = [status.value for status in TERMINAL_STATUSES]

    return (
        db.query(Application)
        .filter(
            and_(
                Application.next_action_date.isnot(None),
                Application.next_action_date <= deadline,
                Application.status.notin_(terminal_values),
            )
        )
        .order_by(Application.next_action_date.asc())
        .all()
    )
