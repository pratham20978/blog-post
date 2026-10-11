# Lab access — Applied Cryptography

> Private build artifact. Read with `plan.md` and `context.md` before every part; re-run the probe.

## Probe — 2026-10-11

```
Linux 7.0.0-38-generic x86_64
Ubuntu 26.04.1 LTS
cpus=16
ram_total=14G ram_available=6G
disk_free=219G on /
nvidia_gpu=none
groups=prathamv adm cdrom sudo dip plugdev lpadmin sambashare
docker=unusable
gcc=yes make=yes uv=yes python3=yes openssl=yes podman=no
python 3.14.4
pyca/cryptography 50.0.0
OpenSSL 3.5.5 27 Jan 2026 (Library: OpenSSL 3.5.5 27 Jan 2026)
```

Everything this series needs is present or user-space installable. Notably **OpenSSL 3.5.5** already
ships ML-KEM (post-quantum KEM), which Part 15 uses, and `cryptography` 50.0.0 covers AES-GCM,
ChaCha20-Poly1305, HKDF, RSA-OAEP/PSS, ECDSA, Ed25519, X25519 and X.509. `argon2-cffi` and any by-hand
toy implementations install into a `uv` venv. The `sudo` group is membership only and is not used.
Docker being unusable does not matter: no part of this series needs a container (contrast the
networking and other security series, which do).

## Requests

None. Every part is **G1 — runs anywhere**, self-provisioned. No hardware, privilege, credential or
gated service is load-bearing for any worked example, figure or claim.

| ID | Need | Parts | Raised | Answer | Answered | Grade as built |
|---|---|---|---|---|---|---|
| — | none | — | — | — | — | G1 throughout |

## Self-provisioned

| What | Where | For | Undo |
|---|---|---|---|
| `uv` venv: `cryptography`≈50.x, `argon2-cffi` (+ toy pure-Python primitives) | `~/.cache/applied-cryptography-lab` | all parts | delete the directory |
| A disposable local CA (OpenSSL: root/intermediate/leaf) | post scratch dir, loopback only | Part 13 | delete generated certs/keys |
| `openssl s_server`/`s_client` on 127.0.0.1 | loopback only | Part 14 | stop the process; nothing persists |

All of the above meet the six self-provision conditions in `references/labs.md`: user-space only, no
root, no account, one directory to delete, well under the RAM/disk headroom, and freshly disposable.

## Capture backlog

None. Nothing is deferred for want of a resource.
