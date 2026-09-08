#!/usr/bin/env bash
# Run backend integration tests in disposable databases on the shared Postgres.
set -euo pipefail

cd "$(dirname -- "${BASH_SOURCE[0]}")/.."

compose=(docker compose --env-file .env)
if [[ -f .env.dev ]]; then
  compose+=(--env-file .env.dev)
fi

"${compose[@]}" -f compose.dev.yaml --profile test run --rm backend-test
