# Canerly blog platform

FastAPI owns typed Markdown ingestion and reader APIs; the Next.js application
lives in the `web` submodule. PostgreSQL stores queryable metadata and MinIO
keeps the canonical Markdown files.

## Isolated development stack

The development overlay reuses the existing `canerly_edge` Postgres and MinIO
services, but targets persistent database `blog-test` and private bucket
`blogs-test`. Only the reader and API bind host ports:

```bash
cp .env.dev.example .env.dev   # optional local overrides
./scripts/dev-up.sh
```

- Reader: `http://localhost:3001`
- API: `http://localhost:8001`

Schema and data changes are explicit one-shot services in this order:
`migrate-dev` → `minio-init-dev`/`metadata-backfill-dev` → `api-dev`/`web-dev`.
Uvicorn does not execute migrations.

Run backend integration tests in a disposable database (never `blog-test`):

```bash
./scripts/dev-test.sh
```

## Real email sign-in

Both the deployed and development APIs use the same provider contract. Put the
secret only in ignored `.env` files, then leave code logging and the fixed
bypass disabled:

```dotenv
BLOGS_EMAIL_PROVIDER=resend
BLOGS_RESEND_API_KEY=<secret>
BLOGS_EMAIL_FROM=Canerly <auth@canery.in>
BLOGS_EMAIL_REPLY_TO=
BLOGS_OTP_LOG_CODES=false
# BLOGS_OTP_DEV_BYPASS_CODE is unset
```

`canery.in` must show as verified in Resend before starting the API. Signup and
login use separate code purposes and email copy; neither code is returned to
the browser or written to logs.

## Metadata rollout

Migration `009` must be applied before the idempotent source backfill. The
backfill is dry-run by default and refuses all writes if any blog cannot be
loaded or parsed:

```bash
python -m blogs.database.migrator up
python -m blogs.database.backfill_metadata
python -m blogs.database.backfill_metadata --apply
```
