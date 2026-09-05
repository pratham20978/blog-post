#!/bin/sh
# Reloads nginx every six hours, so a certificate renewed by the certbot
# container is picked up without anyone remembering to do it. Renewal rewrites
# files nginx has already read into memory; without a reload it keeps serving
# the expired one.
#
# This lives here rather than in the container's `command:` for a reason worth
# keeping. The official entrypoint runs /docker-entrypoint.d/* only when the
# command starts with `nginx`:
#
#     if [ "$1" = "nginx" -o "$1" = "nginx-debug" ]; then ... fi
#     exec "$@"
#
# Overriding the command with a shell one-liner to get this loop therefore
# skipped every init script, 30-enable-tls.sh included — so no site config was
# generated, the image's default.conf stayed in place, and every name served the
# nginx welcome page. The loop belongs on this side of that `if`.
#
# Backgrounded, so this script returns immediately and the entrypoint carries on
# to exec nginx. The loop is reparented to the nginx master and keeps running.

set -eu

(
    while :; do
        sleep 6h
        # Before nginx has written its pid file this is a no-op, which only
        # matters if the container is restarted inside the sleep window.
        nginx -s reload 2>/dev/null || true
    done
) &

echo "40-reload-loop.sh: will reload every 6h to pick up renewed certificates"
