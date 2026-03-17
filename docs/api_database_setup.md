# API + PostgreSQL Setup Guide

This document explains how to create the PostgreSQL database, connect to it, run migrations, start the FastAPI app, perform requests, and deploy to Render.

## 1) Prerequisites

- Python 3.11+
- Docker + Docker Compose
- `psql` client (optional, but useful)

## 2) Configure environment variables (safer setup)

The project **does not hardcode DB credentials in `docker-compose.yml`** anymore.

1. Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

2. Edit `.env` with strong values:

```dotenv
POSTGRES_DB=is_that_a_pix
POSTGRES_USER=is_that_a_pix_user
POSTGRES_PASSWORD=<use-a-strong-password>
# Optional: leave blank to derive from POSTGRES_* instead.
DATABASE_URL=postgresql+psycopg2://is_that_a_pix_user:<use-a-strong-password>@localhost:5432/is_that_a_pix
NOTIFICATION_API_KEY=<use-a-long-random-secret>
ENABLE_DOCS=true
```

3. Keep `.env` private (already ignored by git).

## 3) Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4) Create PostgreSQL database (Docker Compose)

```bash
docker compose up -d db
```

The DB will use the values from your `.env` file.
The published database port is now bound to `127.0.0.1` only.

## 5) Connect to PostgreSQL

Using `psql` directly:

```bash
psql "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}"
```

Using Docker container shell:

```bash
docker exec -it is-that-a-pix-db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

## 6) SQL required for setup

### 6.1 Create database manually (if not using Docker Compose defaults)

```sql
CREATE DATABASE is_that_a_pix;
```

### 6.2 SQL to create `notifications` table

```sql
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    app_name VARCHAR(255) NOT NULL,
    text TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_notifications_id ON notifications (id);
```

### 6.3 Useful SQL checks

```sql
\dt
SELECT * FROM notifications ORDER BY id DESC;
```

## 7) Run Alembic migrations

If `DATABASE_URL` is set in `.env`, just run:

```bash
alembic upgrade head
```

## 8) Run API locally

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Production option with Gunicorn + Uvicorn workers:

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 -w 2
```

## 9) Request example

### Endpoint

- Method: `PUT`
- URL: `http://localhost:8000/record_notification`
- Header: `X-API-Key: <NOTIFICATION_API_KEY>`
- Body:

```json
{
  "app": "99pay",
  "text": "99pay Transação: Valores enviados R$28,50 transferência da sua 99Pay às 12/03/26 20:36:29."
}
```

### cURL request

```bash
curl -X PUT "http://localhost:8000/record_notification" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${NOTIFICATION_API_KEY}" \
  -d '{
    "app": "99pay",
    "text": "99pay Transação: Valores enviados R$28,50 transferência da sua 99Pay às 12/03/26 20:36:29."
  }'
```

Expected behavior:

- `app` and `text` are normalized to lowercase, accents removed, and extra spaces collapsed.
- Data is persisted in `notifications` table.

## 10) Render deployment

1. Push this repository to GitHub.
2. In Render, create a **PostgreSQL** instance.
3. Create a **Web Service** pointing to this repo.
4. Configure environment variables:
   - `DATABASE_URL=<render-postgres-connection-string>`
   - `NOTIFICATION_API_KEY=<long-random-secret>`
   - `ENABLE_DOCS=false`
5. Build command:

```bash
pip install -r requirements.txt
```

6. Start command:

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT -w 2
```

7. Run migrations (Render Shell or Release Command):

```bash
alembic upgrade head
```

8. Test health endpoint:

```bash
curl https://<your-render-service>/health
```

## Security note about `POSTGRES_*` in docker-compose

- Using `POSTGRES_DB` and `POSTGRES_USER` in compose is normal.
- Exposing a real `POSTGRES_PASSWORD` in a committed compose file is a risk.
- Safer pattern: reference environment variables and keep real values in `.env` (not committed), secrets manager, or CI/CD secret store.
- Keep `NOTIFICATION_API_KEY` outside version control as well, and rotate it if a client or machine is compromised.
