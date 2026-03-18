from secrets import compare_digest
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationIn, NotificationOut
from app.services.text_normalizer import normalize_text

router = APIRouter(tags=["notifications"])
PAGE_SIZE = 100


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
        is_financial_transaction=payload.is_financial_notification,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


@router.get(
    "/get_all_notifications",
    response_model=list[NotificationOut],
    dependencies=[Depends(require_notification_api_key)],
)
def get_all_notifications(
    p: Annotated[int, Query(ge=1)] = 1,
    q: str | None = None,
    isft: bool | None = None,
    db: Session = Depends(get_db),
) -> list[Notification]:
    statement = select(Notification)

    if q:
        statement = statement.where(Notification.text.op("~")(normalize_text(q)))

    if isft is not None:
        statement = statement.where(Notification.is_financial_transaction.is_(isft))

    statement = statement.order_by(Notification.id.desc()).offset((p - 1) * PAGE_SIZE).limit(PAGE_SIZE)

    return list(db.scalars(statement).all())
