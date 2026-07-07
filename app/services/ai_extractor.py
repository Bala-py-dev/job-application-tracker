import json
import re
from datetime import timedelta

from app.config import settings
from app.logger import get_logger
from app.models import ApplicationStatus
from app.schemas import ExtractedApplication
from app.utils import utcnow

logger = get_logger(__name__)


STATUS_KEYWORDS = {
    ApplicationStatus.rejected: [
        "unfortunately",
        "not moving forward",
        "will not be proceeding",
        "regret to inform",
        "other candidates",
    ],
    ApplicationStatus.interview: [
        "interview",
        "schedule a call",
        "meet the team",
        "technical round",
    ],
    ApplicationStatus.screening: [
        "screening",
        "phone screen",
        "recruiter call",
        "initial call",
    ],
    ApplicationStatus.offer: [
        "offer",
        "pleased to offer",
        "compensation package",
    ],
    ApplicationStatus.applied: [
        "we received your application",
        "thank you for applying",
        "application has been received",
    ],
}


def _guess_status(text: str) -> ApplicationStatus:
    lowered = text.lower()
    for status, keywords in STATUS_KEYWORDS.items():
        for keyword in keywords:
            if keyword in lowered:
                return status
    return ApplicationStatus.applied


def _guess_company(text: str) -> str | None:
    match = re.search(
        r"(?:at|from|with|join|to)\s+([A-Z][A-Za-z0-9&\-]+(?:\s+[A-Z][A-Za-z0-9&\-]+){0,2})",
        text,
    )
    if match:
        return match.group(1).strip().rstrip(".")
    return None


def _guess_role(text: str) -> str | None:
    before = re.search(
        r"((?:[A-Z][A-Za-z0-9/\-]+\s+){1,4})(?:position|role)\b", text
    )
    if before:
        return before.group(1).strip()

    after = re.search(
        r"(?:position|role)\s+of\s+((?:[A-Z][A-Za-z0-9/\-]+\s*){1,4})", text
    )
    if after:
        return after.group(1).strip()

    return None


def _rule_based_extract(text: str) -> ExtractedApplication:
    status = _guess_status(text)
    next_action = None
    next_action_date = None

    if status == ApplicationStatus.interview:
        next_action = "Prepare for interview"
        next_action_date = utcnow() + timedelta(
            days=settings.reminder_default_days
        )
    elif status in (ApplicationStatus.applied, ApplicationStatus.screening):
        next_action = "Follow up on application"
        next_action_date = utcnow() + timedelta(
            days=settings.reminder_default_days
        )

    return ExtractedApplication(
        company=_guess_company(text),
        role=_guess_role(text),
        status=status,
        next_action=next_action,
        next_action_date=next_action_date,
    )


def _openai_extract(text: str) -> ExtractedApplication:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)

    prompt = (
        "Extract job application details from the email below. "
        "Return only JSON with keys: company, role, status, next_action. "
        "status must be one of: applied, screening, interview, offer, rejected, accepted, withdrawn.\n\n"
        f"Email:\n{text}"
    )

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    data = json.loads(response.choices[0].message.content)

    status_value = data.get("status")
    status = None
    if status_value in ApplicationStatus.__members__:
        status = ApplicationStatus(status_value)

    next_action = data.get("next_action")
    next_action_date = None
    if next_action:
        next_action_date = utcnow() + timedelta(
            days=settings.reminder_default_days
        )

    return ExtractedApplication(
        company=data.get("company"),
        role=data.get("role"),
        status=status,
        next_action=next_action,
        next_action_date=next_action_date,
    )


def extract_from_email(text: str) -> ExtractedApplication:
    if settings.openai_api_key:
        try:
            logger.info("Extracting application details using OpenAI")
            return _openai_extract(text)
        except Exception as error:
            logger.warning("OpenAI extraction failed, using rule-based fallback: %s", error)

    logger.info("Extracting application details using rule-based parser")
    return _rule_based_extract(text)
