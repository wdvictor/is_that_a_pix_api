from pydantic import BaseModel, Field


class NotificationIn(BaseModel):
    app: str = Field(min_length=1, max_length=255)
    text: str = Field(min_length=1, max_length=4096)


class NotificationOut(BaseModel):
    id: int
    app_name: str
    text: str

    class Config:
        from_attributes = True
