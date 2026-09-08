#!/usr/bin/env bash
# Start the isolated reader/API development stack on the existing private network.
set -euo pipefail

cd "$(dirname -- "${BASH_SOURCE[0]}")/.."

compose=(docker compose --env-file .env)
if [[ -f .env.dev ]]; then
  compose+=(--env-file .env.dev)
fi

"${compose[@]}" -f compose.dev.yaml up -d --build
"${compose[@]}" -f compose.dev.yaml ps

printf 'Web: http://localhost:3001\nAPI: http://localhost:8001\n'
