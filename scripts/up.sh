#!/usr/bin/env bash
#
# Brings the whole site up: nginx, the reader site, the API, Postgres, MinIO,
# pgAdmin, and the Cloudflare Tunnel that makes any of it reachable. Run from
# anywhere, without sudo.
#
#   ./scripts/up.sh              # pull what's new, then start everything
#   PULL=0 ./scripts/up.sh       # start with the images already on this machine
#
# Safe to run repeatedly, and the right thing to run after a reboot — the
# containers restart on their own if the Docker daemon is enabled at boot
# (`sudo systemctl enable docker`), and this puts them right if it is not.
#
# Portainer is not touched — it keeps running as it already does, and nginx
# proxies to it.
#
set -euo pipefail
# shellcheck source=scripts/_docker.sh
source "$(dirname -- "${BASH_SOURCE[0]}")/_docker.sh"

# The tunnel is the only route in from the internet, and a missing config here
# is the one failure that leaves every container healthy while every public name
# answers Cloudflare error 1033. Worse, Docker would bind-mount the missing path
# by creating a *directory* called config.yml, which then has to be deleted by
# hand. Caught before starting rather than diagnosed afterwards.
if [[ ! -f deploy/cloudflared/config.yml ]]; then
  [[ -d deploy/cloudflared/config.yml ]] && rm -rf deploy/cloudflared/config.yml
  fail "deploy/cloudflared/config.yml is missing. Run ./scripts/tunnel-setup.sh first."
fi

creds_name="$(sed -n 's#^credentials-file: /etc/cloudflared/creds/##p' deploy/cloudflared/config.yml)"
if [[ -z "$creds_name" || ! -f "deploy/cloudflared/creds/$creds_name" ]]; then
  fail "the tunnel's credentials are missing. Run ./scripts/tunnel-setup.sh — on a fresh
clone it reissues them for the existing tunnel rather than creating a new one."
fi

if [[ "${PULL:-1}" == "1" ]]; then
  bold "Pulling images"
  "${compose[@]}" pull --quiet
fi

bold "Starting"
# Migrations run first as their own container and the API waits on the exit
# code, so a failed migration stops the deploy instead of half-applying under a
# running site.
"${compose[@]}" up -d --remove-orphans

bold "Status"
"${compose[@]}" ps

domain="$(sed -n 's/^DOMAIN=//p' .env | tail -1)"
domain="${domain:-canery.in}"

# Whatever the browser gets, which is not what nginx serves: Cloudflare
# terminates TLS at its edge and the tunnel carries plain HTTP the rest of the
# way. Nothing here inspects nginx for a certificate, because there isn't one
# and there should not be.
scheme="$(sed -n 's/^PUBLIC_SCHEME=//p' .env | tail -1)"
scheme="${scheme:-https}"

if ! "${compose[@]}" ps --status running --services 2>/dev/null | grep -qx cloudflared; then
  warn "cloudflared is not running — these names will answer with Cloudflare error 1033 until it is."
fi

bold "Up"
for name in "" api. pgadmin. minioview. minio. portainer.; do
  printf '  %s://%s%s\n' "$scheme" "$name" "$domain"
done
