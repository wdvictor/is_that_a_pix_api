from secrets import compare_digest
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationIn, NotificationOut, NotificationUpdateIn
from app.services.text_normalizer import normalize_text

router = APIRouter(tags=["notifications"])
DEFAULT_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1
MAX_PAGE_SIZE = 2000


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


@router.put(
    "/update_notification",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_notification_api_key)],
)
def update_notification(
    payload: NotificationUpdateIn,
    db: Session = Depends(get_db),
) -> Response:
    notification = db.get(Notification, payload.id)

    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="notification not found")

    notification.is_financial_transaction = payload.is_financial_transaction
    db.commit()

    return Response(status_code=status.HTTP_200_OK)


@router.delete(
    "/delete_notification",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_notification_api_key)],
)
def delete_notification(
    id: Annotated[int, Query(gt=0)],
    db: Session = Depends(get_db),
) -> Response:
    notification = db.get(Notification, id)

    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="notification not found")

    db.delete(notification)
    db.commit()

    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/get_all_notifications",
    response_model=list[NotificationOut],
    dependencies=[Depends(require_notification_api_key)],
)
def get_all_notifications(
    p: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    q: str | None = None,
    isft: bool | None = None,
    db: Session = Depends(get_db),
) -> list[Notification]:
    statement = select(Notification)

    if q:
        statement = statement.where(Notification.text.op("~")(normalize_text(q)))

    if isft is None:
        statement = statement.where(Notification.is_financial_transaction.is_(None))
    else:
        statement = statement.where(Notification.is_financial_transaction.is_(isft))

    statement = statement.order_by(Notification.id.desc()).offset((p - 1) * size).limit(size)

    return list(db.scalars(statement).all())
