#!/usr/bin/env bash
# Apply database migrations explicitly. The legacy Markdown metadata backfill
# is opt-in because it requires every database row to have a readable object in
# MinIO and is not part of normal application startup.
set -euo pipefail

# shellcheck source=scripts/_docker.sh
source "$(dirname -- "${BASH_SOURCE[0]}")/_docker.sh"

with_metadata_backfill=0
target=production

usage() {
  cat <<'EOF'
Usage: ./scripts/migrate.sh [--dev] [--metadata-backfill]

  (no options)          Apply pending production SQL migrations.
  --dev                 Target blog-test and blogs-test via compose.dev.yaml.
  --metadata-backfill   Validate every stored Markdown object, then apply the
                        one-time typed metadata backfill.
EOF
}

while (($#)); do
  case "$1" in
    --dev) target=development ;;
    --metadata-backfill) with_metadata_backfill=1 ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; fail "unknown option: $1" ;;
  esac
  shift
done

service=migrate
backfill_service=metadata-backfill
minio_init_service=minio-init

if [[ "$target" == development ]]; then
  compose+=(--env-file .env)
  [[ -f .env.dev ]] && compose+=(--env-file .env.dev)
  compose+=(-f compose.dev.yaml)
  service=migrate-dev
  backfill_service=metadata-backfill-dev
  minio_init_service=minio-init-dev
fi

bold "Applying ${target} database migrations"
"${compose[@]}" --profile maintenance run --rm "$service"

if ((with_metadata_backfill == 0)); then
  bold "Migration complete"
  printf 'Metadata backfill was not run. Use --metadata-backfill only for the legacy metadata rollout.\n'
  exit 0
fi

bold "Preparing the private Markdown bucket"
"${compose[@]}" run --rm "$minio_init_service"

bold "Validating stored Markdown metadata"
"${compose[@]}" --profile maintenance run --rm --no-deps "$backfill_service"

bold "Applying stored Markdown metadata"
"${compose[@]}" --profile maintenance run --rm --no-deps \
  "$backfill_service" python -m blogs.database.backfill_metadata --apply

bold "Migration and metadata backfill complete"
