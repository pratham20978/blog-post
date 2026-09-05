#!/usr/bin/env bash
#
# Builds both images and pushes them to their own Docker Hub repositories:
#
#   .      -> $NAMESPACE/blog-backend    (FastAPI, src/blogs)
#   ./web  -> $NAMESPACE/blog-ui         (Next.js)
#
# Run it from anywhere, without sudo — it escalates per command where it has to.
#
#   ./scripts/publish.sh
#   NEXT_PUBLIC_SITE_URL=https://canery.in ./scripts/publish.sh
#   TAG=v1.4.0 ./scripts/publish.sh
#   PUSH=0 ./scripts/publish.sh          # build only, push nothing
#
set -euo pipefail

NAMESPACE="${NAMESPACE:-prathamverma0803}"
BACKEND_REPO="$NAMESPACE/blog-backend"
UI_REPO="$NAMESPACE/blog-ui"
PUSH="${PUSH:-1}"

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bold() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
fail() { printf '\033[31merror: %s\033[0m\n' "$*" >&2; exit 1; }

# The Hub credentials live in the invoking user's config, not root's. A bare
# `sudo docker push` therefore pushes anonymously and Docker Hub rejects it as
# `insufficient_scope`, so sudo is pointed back at that same config. None of
# this applies once the user is in the `docker` group — then plain docker works
# and already reads the right file.
if [[ -n "${SUDO_USER:-}" ]]; then
  user_home="$(getent passwd "$SUDO_USER" | cut -d: -f6)"
else
  user_home="$HOME"
fi

if docker info >/dev/null 2>&1; then
  docker_cmd=(docker)
else
  docker_cmd=(sudo docker --config "$user_home/.docker")
  bold "Docker needs sudo here; using credentials from $user_home/.docker"
fi

[[ -f "$user_home/.docker/config.json" ]] ||
  fail "not logged in — run: docker login -u $NAMESPACE"

# Each image carries `latest` plus an immutable tag, because `latest` is
# overwritten on every push and a rollback needs something that is not.
backend_tag="${TAG:-$(sed -n 's/^version = "\(.*\)"/\1/p' pyproject.toml | head -1)}"
ui_tag="${TAG:-$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' web/package.json | head -1)}"
[[ -n "$backend_tag" ]] || fail "could not read version from pyproject.toml"
[[ -n "$ui_tag" ]] || fail "could not read version from web/package.json"

# NEXT_PUBLIC_ values are compiled into the browser bundle, so they are fixed
# when the image is built and cannot be changed by `docker run`. Left at the
# default, the pushed image tells every visitor the site lives on localhost.
site_url="${NEXT_PUBLIC_SITE_URL:-http://localhost:3000}"
if [[ "$site_url" == *localhost* && "$PUSH" == "1" ]]; then
  printf '\033[33mwarning: building blog-ui with NEXT_PUBLIC_SITE_URL=%s\033[0m\n' "$site_url"
  printf '         Baked in at build time. Re-run with the real origin to fix.\n'
fi

bold "Building $BACKEND_REPO:$backend_tag"
"${docker_cmd[@]}" build \
  -t "$BACKEND_REPO:latest" \
  -t "$BACKEND_REPO:$backend_tag" \
  .

bold "Building $UI_REPO:$ui_tag"
"${docker_cmd[@]}" build \
  --build-arg NEXT_PUBLIC_SITE_URL="$site_url" \
  --build-arg NEXT_PUBLIC_SITE_NAME="${NEXT_PUBLIC_SITE_NAME:-Canerly}" \
  --build-arg NEXT_PUBLIC_SEARCH_ADAPTER="${NEXT_PUBLIC_SEARCH_ADAPTER:-none}" \
  --build-arg NEXT_PUBLIC_OAUTH_PROVIDERS="${NEXT_PUBLIC_OAUTH_PROVIDERS:-}" \
  -t "$UI_REPO:latest" \
  -t "$UI_REPO:$ui_tag" \
  ./web

if [[ "$PUSH" != "1" ]]; then
  bold "Built both images. PUSH=0, so nothing was pushed."
  exit 0
fi

# Both images build before either is pushed: a failure in the second build
# should not leave the registry holding half a release.
for ref in "$BACKEND_REPO:latest" "$BACKEND_REPO:$backend_tag" \
           "$UI_REPO:latest" "$UI_REPO:$ui_tag"; do
  bold "Pushing $ref"
  "${docker_cmd[@]}" push "$ref"
done

bold "Done"
printf '  %s\n  %s\n  %s\n  %s\n' \
  "$BACKEND_REPO:latest" "$BACKEND_REPO:$backend_tag" \
  "$UI_REPO:latest" "$UI_REPO:$ui_tag"
