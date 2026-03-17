from fastapi import FastAPI

from app.api.notifications import router as notifications_router
from app.core.config import settings

docs_url = "/docs" if settings.enable_docs else None
openapi_url = "/openapi.json" if settings.enable_docs else None

app = FastAPI(title="Is That a Pix API", docs_url=docs_url, redoc_url=None, openapi_url=openapi_url)
app.include_router(notifications_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
