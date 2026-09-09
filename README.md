# Canerly blog platform

FastAPI owns typed Markdown ingestion and reader APIs; the Next.js application
lives in the `web` submodule. PostgreSQL stores queryable metadata and MinIO
keeps the canonical Markdown files.

## Interactive blog administration

Use the terminal admin tool instead of rebuilding multipart `curl` commands or
copying access tokens by hand:

```bash
./scripts/blog-admin.sh
```

Press Enter at the target prompt to use `https://api.canery.in`. The tool reads
the secret admin route and admin email from `.env`, prompts for the password
without echoing it, signs in, and manages the access token for the current run.
It can publish Markdown (frontmatter plus optional field overrides), upsert and
list categories/series, list blogs, archive blogs, and delete taxonomy entries.
Deleting an assigned category is refused; deleting a series leaves its blogs
intact and removes only their series assignment.

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

## Reader engagement and announcements

Migration `010` starts qualified view counters at zero, adds member likes and
creates durable announcement campaigns. Apply it before deploying the API and
web, then run the outbox worker as its own process:

```bash
python -m blogs.database.migrator up
python -m blogs.workers.outbox
```

The worker uses the same Resend configuration as OTP delivery. Publication is
not coupled to email availability; failed deliveries are leased and retried,
and readers can manage new-blog email preferences from their profile.
