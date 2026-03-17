from secrets import compare_digest
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationIn, NotificationOut
from app.services.text_normalizer import normalize_text

router = APIRouter(tags=["notifications"])


def require_notification_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
    if x_api_key and compare_digest(x_api_key, settings.notification_api_key):
        return
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid api key")


@router.put(
    "/add_notification",
    response_model=NotificationOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_notification_api_key)],
)
def add_notification(payload: NotificationIn, db: Session = Depends(get_db)) -> Notification:
    notification = Notification(
        app_name=normalize_text(payload.app),
        text=normalize_text(payload.text),
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
