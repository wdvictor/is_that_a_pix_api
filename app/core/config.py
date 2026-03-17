import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    app_name: str = "is-that-a-pix-api"
    database_url: str
    notification_api_key: str = Field(min_length=16)
    enable_docs: bool = False


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(f"{name} is required")


def _get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _build_database_url() -> str:
    direct_url = os.getenv("DATABASE_URL")
    if direct_url:
        return direct_url

    db_name = _get_required_env("POSTGRES_DB")
    db_user = _get_required_env("POSTGRES_USER")
    db_password = quote_plus(_get_required_env("POSTGRES_PASSWORD"))
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")

    return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


settings = Settings(
    database_url=_build_database_url(),
    notification_api_key=_get_required_env("NOTIFICATION_API_KEY"),
    enable_docs=_get_bool_env("ENABLE_DOCS", default=False),
)
