# Deploying canery.in from this machine

Five public names, one certificate, one command.

| Name | Serves |
|---|---|
| `canery.in`, `www.canery.in` | the reader site (Next.js) |
| `api.canery.in` | the FastAPI backend |
| `pgadmin.canery.in` | pgAdmin — the only route to Postgres from outside |
| `minioview.canery.in` | the MinIO console |
| `minio.canery.in` | public object reads — the `media` bucket only, GET and HEAD only |
| `portainer.canery.in` | the Portainer already running on this host |

Postgres is **not** published. It is reachable on the private Docker network as
`db:5432` and nowhere else. That is what makes it safe to point a public domain
at a machine on your desk; adding a `ports:` entry to it silently undoes it.

MinIO is published, but only through a keyhole. See below.

## The two buckets

This is the one piece of the design worth understanding before you use it.

| Bucket | Holds | Reachable from the internet |
|---|---|---|
| `blogs` | article Markdown, **drafts included** | no |
| `media` | images and files meant to be linked directly | yes, read-only |

`minio.canery.in` serves `/media/` and returns 404 for everything else — the
other bucket, the S3 admin API, the console. It allows GET and HEAD, nothing
more. A blanket proxy to `:9000` would instead have published every unpublished
draft to anyone who guessed a key, and a key being hard to guess is not access
control.

So: an `<img src="https://minio.canery.in/media/…">` works, and nothing you
write to the `blogs` bucket can ever be fetched that way.

The backend does not use this door. It talks to `minio:9000` over the private
network, which is why `BLOGS_OBJECT_STORE_SECURE=false` is correct — that
setting governs the backend's own hop to storage, not what the browser gets, and
that hop never leaves the machine. It would only need to be `true` if the
backend's endpoint were itself a public hostname.

## Putting an image in an article

Markdown stores a **link**, never the bytes — so the image has to exist at a URL
before the article can reference it. The upload is a separate act, done by hand
through the console:

1. Open `minioview.canery.in` and sign in with
   `BLOGS_OBJECT_STORE_ACCESS_KEY` / `BLOGS_OBJECT_STORE_SECRET_KEY` from `.env`.
2. Upload into the **`media`** bucket. Not `blogs` — an image put there is
   unreachable from the internet, and every article referencing it shows a
   broken image with a 404 that looks like a proxy fault.
3. The public URL is `https://minio.canery.in/media/<path you uploaded to>`.
   Build it yourself from the object's path.
4. Reference it: `![alt text](https://minio.canery.in/media/covers/thing.png)`

**Do not use the console's Share button.** It generates a presigned URL —
signed, and expiring in seven days at the outside. Pasted into an article, it
works all through review and then goes dead. The plain URL in step 3 has no
signature and no expiry, which is the entire reason the `media` bucket is
anonymous-readable.

One ordering note: an object is public the moment it is uploaded,
before any article links to it; there is no draft state for a file in `media`.

**Still to write, in application code:** nothing uploads to `media` yet. The
only writer today is [`blog_service.py`](../src/blogs/services/blog_service.py),
which puts Markdown into `blogs`. An image upload path needs a second
`MinioObjectStore` pointed at the `media` bucket, and something that turns a
stored key into `https://minio.canery.in/media/<key>`. `presign_get` is not the
answer for public images — a presigned URL expires, which breaks any article
whose cover has been shared or cached.

## Once, before the first deploy

**1. Fill in `.env`.** Copy the deployment block from `.env.example` and set
every empty value. Passwords are needed for Postgres, pgAdmin and MinIO — MinIO
refuses a root password shorter than 8 characters.

```bash
openssl rand -base64 24        # one of these per password
```

`BLOGS_OBJECT_STORE_ACCESS_KEY` and `BLOGS_OBJECT_STORE_SECRET_KEY` become
MinIO's root credentials as well as the backend's — one pair, so they cannot
drift apart.

**2. Rebuild the UI image with the real origin.** `NEXT_PUBLIC_SITE_URL` is
compiled into the browser bundle when the image is built and cannot be changed
by `docker run`. The image on Docker Hub right now says `http://localhost:3000`.

```bash
NEXT_PUBLIC_SITE_URL=https://canery.in ./scripts/publish.sh
```

**3. Create the tunnel.**

```bash
./scripts/tunnel-setup.sh
```

Once, and idempotent. It authorises against Cloudflare in a browser, creates the
tunnel, writes `deploy/cloudflared/config.yml`, and points all seven names at it.

Prerequisites are the domain being on Cloudflare with its nameservers changed —
nothing else. In particular it does **not** need the Zero Trust dashboard, which
demands a payment method before it will show you its Tunnels page even on the
free plan. The CLI produces the same tunnel without one.

There is deliberately no record for `db` — Postgres publishes no port, so the
name would only advertise a service that is not there.

**No A records, and no IP address anywhere.** Each name becomes a proxied CNAME
to `<uuid>.cfargotunnel.com`, which resolves only inside Cloudflare's network and
means "whichever connector is attached right now". That is the whole point: an A
record is a claim about where this machine sits, and it is wrong the moment the
laptop moves. A private address like `192.168.0.106` is a claim every device
outside this house reads as "somewhere on my own network"; a home public IP is
one the ISP revokes on its own schedule. The tunnel makes no such claim, so
moving to another wifi network — or a phone hotspot, where carrier-grade NAT
makes inbound connections impossible altogether — changes nothing.

**4. Do not forward any ports.** Nothing here listens for inbound connections;
`cloudflared` dials outward and traffic returns down that pipe. If 80 and 443
were forwarded for an earlier attempt, remove those rules — they are now a way
in that nothing needs.

## Bringing it up

```bash
./scripts/up.sh
```

Pulls, starts everything in dependency order, and prints where each site is.
Migrations run first, in their own container, and the API waits on the exit
code — a failed migration stops the deploy rather than half-applying underneath
a running site.

It refuses to start if the tunnel configuration or its credentials are missing,
rather than bringing up a stack that is healthy in every way except being
reachable.

**After a reboot there is nothing to do.** Every service is
`restart: unless-stopped`, so Docker brings them back by itself — provided the
daemon starts at boot:

```bash
sudo systemctl enable docker      # once, per machine
```

If it does not, or if anything looks wrong, `./scripts/up.sh` is the answer. It
is idempotent: running it against a healthy stack changes nothing.

To prove the machine itself is serving correctly, independently of Cloudflare:

```bash
curl -H 'Host: api.canery.in' http://localhost/healthz
curl -H 'Host: canery.in'     http://localhost/ -I
```

And end to end, through the tunnel:

```bash
curl -sS https://api.canery.in/healthz
```

## HTTPS

Already on, and there is nothing to do. Cloudflare terminates TLS at its edge
and issues that certificate itself. `PUBLIC_SCHEME=https` in `.env` reflects what
the browser gets, not what nginx serves — inside the tunnel it is plain HTTP, and
that hop never leaves the Docker network.

**Never obtain a Let's Encrypt certificate for these names.** It is not merely
redundant, it is an outage. `30-enable-tls.sh` switches nginx to the config that
redirects HTTP to HTTPS the moment one appears in `certbot-conf`; `cloudflared`
speaks HTTP to nginx, so the redirect would send the request back around the
tunnel into itself. `scripts/issue-certs.sh` has been deleted for this reason and
there is no certbot service any more.

In the Cloudflare dashboard, **SSL/TLS → Full (strict)** is the correct mode for
a tunnel.

## Moving to another machine

Almost nothing to redo. The domain work was one-time and lives at Cloudflare, not
here.

**Never again, on any machine:**

- GoDaddy. The nameservers point at Cloudflare and that is a registrar setting,
  not a machine one. Do not go back for anything.
- The seven DNS records. They are CNAMEs to the tunnel's UUID, and the tunnel
  outlives the machine that runs it.
- Creating the tunnel. It already exists in your Cloudflare account.
- Ports, firewalls, IP addresses. There are none to configure, which is the
  entire reason this survives a change of machine.

**What the new machine needs**, in order:

```bash
# 1. Docker, and cloudflared for the setup script
sudo systemctl enable docker
curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o /tmp/cloudflared.deb
sudo dpkg -i /tmp/cloudflared.deb

# 2. The code — --recurse-submodules, or web/ arrives empty
git clone --recurse-submodules <repo> && cd blog-post

# 3. .env — copy it from the old machine. It is git-ignored, and it is the
#    only thing here that cannot be regenerated. Without the same
#    BLOGS_OBJECT_STORE_* pair MinIO will not open its existing data, and
#    without the same BLOGS_JWT_SECRET every signed-in reader is logged out.

# 4. The tunnel. Opens a browser to authorise, finds the existing tunnel, and
#    reissues its credentials — it does not create a second one.
./scripts/tunnel-setup.sh

# 5. Up
./scripts/up.sh
```

**Stop the old machine first.** Two connectors on one tunnel is a supported
configuration — Cloudflare load-balances across them — which here means requests
landing on two different databases at random, with no error anywhere to explain
it. `docker compose down` on the old machine before `up.sh` on the new one.

**The data does not travel with the code.** `pgdata` and `miniodata` are Docker
volumes on the old machine; a clone brings neither. Migrations will build an
empty schema and the site will come up looking like a fresh install. Move them
deliberately:

```bash
# on the old machine
docker compose exec -T db pg_dump -U "$POSTGRES_USER" blogs > blogs.sql
docker run --rm -v canerly_miniodata:/data -v "$PWD":/out alpine \
    tar czf /out/miniodata.tar.gz -C /data .

# on the new one, after ./scripts/up.sh has created the volumes
docker compose exec -T db psql -U "$POSTGRES_USER" blogs < blogs.sql
docker run --rm -v canerly_miniodata:/data -v "$PWD":/in alpine \
    tar xzf /in/miniodata.tar.gz -C /data
docker compose restart minio
```

## Everyday operations

```bash
./scripts/up.sh                                  # deploy the current images
docker compose logs -f api                       # follow one service
docker compose ps                                # what is healthy
docker compose run --rm migrate                  # re-run migrations alone
docker compose down                              # stop (volumes survive)
```

Data lives in named volumes — `pgdata`, `miniodata`, `pgadmindata`,
`certbot-conf`. `docker compose down` keeps them. `docker compose down -v`
deletes them, database included. There is no backup here yet.

**Connecting pgAdmin to the database:** host `db`, port `5432`, and the
`POSTGRES_*` credentials from `.env`. Not `localhost` — pgAdmin is a container,
and `localhost` there is pgAdmin itself.

**Reaching Postgres from your laptop:** there is no public port, by choice. Use
an SSH tunnel.

```bash
ssh -L 5432:localhost:5432 you@this-machine
```

That needs the port published to the host loopback, which it currently is not —
add `ports: ["127.0.0.1:5432:5432"]` to the `db` service if you want it. Bound
to `127.0.0.1`, not `0.0.0.0`, or it is on the internet again.

## What this deploy is not

**It is staging, not production.** `BLOGS_ENVIRONMENT=local`, so the OTP dev
bypass code still works and sign-in codes are written to the API log. That is
deliberate — `BLOGS_EMAIL_PROVIDER=none` means no mail is sent, so without the
bypass nobody could sign in at all except through Google or GitHub.

`BLOGS_DEBUG` is forced to `false` in `compose.yaml` regardless, because
`api.canery.in` is public and debug mode serves `/docs` and allows every CORS
origin.

Going to production later means, in one sitting: a real email provider, then
`BLOGS_ENVIRONMENT=production` — which makes the app **refuse to start** until
`BLOGS_JWT_SECRET`, `BLOGS_ACTOR_TOKEN_SECRET` and `BLOGS_OTP_PEPPER` are all
set to non-default values, `BLOGS_OTP_LOG_CODES=false`,
`BLOGS_OTP_DEV_BYPASS_CODE` is removed entirely, and `BLOGS_ADMIN_PATH_PREFIX`
is at least 16 unguessable characters.

**There are no backups.** A `pg_dump` on a timer is the obvious next thing, and
`miniodata` needs one too now that it holds media nothing else has a copy of.

**Anything in the `media` bucket is public.** It is served without
authentication to anyone with the URL — that is the point of it. Treat it as a
CDN origin, not as storage: nothing private, ever, and no assumption that a
key is secret because it is long.
