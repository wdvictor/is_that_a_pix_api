from pydantic import BaseModel, Field


class NotificationIn(BaseModel):
    app: str = Field(min_length=1, max_length=255)
    text: str = Field(min_length=1, max_length=4096)
    is_financial_notification: bool | None = None


class NotificationOut(BaseModel):
    id: int
    app_name: str
    text: str
    is_financial_transaction: bool | None

    class Config:
        from_attributes = True
