# Sourced, not run. Sets `compose` to a Docker Compose invocation that works
# whether or not this user can reach the Docker socket, and puts the caller in
# the repository root.
#
# The real fix is to stop needing sudo at all:
#
#   sudo usermod -aG docker "$USER"     # then log out and back in
#
# Until then, sudo is pointed back at the invoking user's Docker config, because
# the Hub credentials live there and not in root's.

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

bold() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
warn() { printf '\033[33mwarning: %s\033[0m\n' "$*" >&2; }
fail() { printf '\033[31merror: %s\033[0m\n' "$*" >&2; exit 1; }

if [[ -n "${SUDO_USER:-}" ]]; then
  user_home="$(getent passwd "$SUDO_USER" | cut -d: -f6)"
else
  user_home="$HOME"
fi

if docker info >/dev/null 2>&1; then
  compose=(docker compose)
else
  compose=(sudo docker --config "$user_home/.docker" compose)
fi

[[ -f .env ]] || fail ".env not found. Copy .env.example to .env and fill it in."
