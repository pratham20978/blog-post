#!/bin/sh
# Picks the HTTP or the HTTPS site configuration at container start.
#
# nginx refuses to start when an ssl_certificate path does not exist, which is
# the chicken-and-egg at the heart of every certbot setup: the certificate is
# fetched over HTTP by a server that will not boot without the certificate.
# Choosing the config at start time breaks the cycle, so `up` works on a machine
# that has never held a certificate, and the same command serves HTTPS the next
# time round.
#
# The official nginx image runs everything executable in /docker-entrypoint.d
# in name order before starting nginx. 20-envsubst-on-templates.sh, which runs
# just before this, only looks at /etc/nginx/templates — a different directory
# from the /etc/nginx/site-templates used here, so the two do not collide.

set -eu

me="30-enable-tls.sh"

if [ -z "${DOMAIN:-}" ]; then
    echo "$me: DOMAIN is not set; refusing to generate a site configuration" >&2
    exit 1
fi

# The image ships a welcome page bound to :80 as the default server. Left in
# place it answers for every name we do not explicitly claim.
rm -f /etc/nginx/conf.d/default.conf

if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    template=/etc/nginx/site-templates/tls.conf.template
    echo "$me: certificate found for $DOMAIN — serving HTTPS"
    echo "$me: WARNING — behind Cloudflare Tunnel this breaks the site. The TLS"
    echo "$me: config redirects HTTP to HTTPS, and cloudflared speaks HTTP to us,"
    echo "$me: so requests loop back around the tunnel. Delete the certificate."
else
    template=/etc/nginx/site-templates/http.conf.template
    echo "$me: no certificate for $DOMAIN — serving plain HTTP, which is correct"
    echo "$me: behind Cloudflare Tunnel: TLS is terminated at Cloudflare's edge."
fi

# An explicit variable list, because the configuration is full of nginx's own
# $host, $scheme and $connection_upgrade — an unrestricted envsubst would blank
# every one of them.
envsubst '${DOMAIN}' < "$template" > /etc/nginx/conf.d/sites.conf
