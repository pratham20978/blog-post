#!/usr/bin/env bash
# Interactive administration for Canery blogs, categories, and series.
#
# The tool signs in through the existing secret admin route and keeps the
# resulting access token only in a private temporary curl config. It never
# writes credentials back to the repository or to shell history.
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

readonly canery_api_default="https://api.canery.in"
readonly dev_api_default="http://127.0.0.1:8001"
readonly local_api_default="http://127.0.0.1:8000"

api_base=""
admin_prefix=""
admin_root=""
admin_email=""
admin_password=""
access_token=""
target_name=""
response_file=""
auth_config=""
last_http_status=""

bold() { printf '\n\033[1m%s\033[0m\n' "$*"; }
info() { printf '\033[36m%s\033[0m\n' "$*"; }
warn() { printf '\033[33mwarning: %s\033[0m\n' "$*" >&2; }
fail() { printf '\033[31merror: %s\033[0m\n' "$*" >&2; exit 1; }

usage() {
  cat <<'EOF'
Usage: ./scripts/blog-admin.sh

Interactive admin tool for:
  - publishing a Markdown blog
  - creating or updating a category
  - creating or updating a series
  - listing blogs, categories, and series
  - archiving a blog or deleting a category/series

The default target is https://api.canery.in. Configuration is read from the
current environment first and then from .env (and .env.dev for the dev target):

  BLOG_ADMIN_API_URL          Override the selected target URL
  BLOG_ADMIN_PATH_PREFIX      Override BLOGS_ADMIN_PATH_PREFIX for this tool
  BLOG_ADMIN_ACCESS_TOKEN     Use an existing admin access token
  BLOG_ADMIN_EMAIL            Override BLOGS_ADMIN_EMAIL
  BLOG_ADMIN_PASSWORD         Avoid the hidden password prompt (prefer prompt)

Tokens and passwords are never persisted after this script exits.
EOF
}

cleanup() {
  access_token=""
  admin_password=""
  if [[ -n "${tool_tmp_dir:-}" && -d "$tool_tmp_dir" ]]; then
    rm -rf -- "$tool_tmp_dir"
  fi
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi
[[ $# -eq 0 ]] || fail "unknown argument: $1 (use --help)"
[[ -t 0 ]] || fail "this tool is interactive and must be run from a terminal"

for dependency in curl jq; do
  command -v "$dependency" >/dev/null 2>&1 || fail "$dependency is required"
done

tool_tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/canery-blog-admin.XXXXXX")"
chmod 700 "$tool_tmp_dir"
response_file="$tool_tmp_dir/response.json"
auth_config="$tool_tmp_dir/auth.curl"
trap cleanup EXIT

prompt() {
  local variable_name="$1"
  local label="$2"
  local default_value="${3:-}"
  local answer

  if [[ -n "$default_value" ]]; then
    printf '%s [%s]: ' "$label" "$default_value"
  else
    printf '%s: ' "$label"
  fi
  if ! IFS= read -r answer; then
    printf '\n'
    exit 0
  fi
  printf -v "$variable_name" '%s' "${answer:-$default_value}"
}

prompt_secret() {
  local variable_name="$1"
  local label="$2"
  local answer

  printf '%s: ' "$label"
  if ! IFS= read -r -s answer; then
    printf '\n'
    exit 0
  fi
  printf '\n'
  printf -v "$variable_name" '%s' "$answer"
}

confirm_exact() {
  local expected="$1"
  local label="$2"
  local answer
  printf '%s\nType %q to confirm: ' "$label" "$expected"
  IFS= read -r answer || return 1
  [[ "$answer" == "$expected" ]]
}

# Read dotenv as data, never by sourcing it as shell code. The last matching
# assignment wins, mirroring common dotenv behaviour without evaluating values.
dotenv_value() {
  local key="$1"
  shift
  local file line value="" found=0

  for file in "$@"; do
    [[ -f "$file" ]] || continue
    while IFS= read -r line || [[ -n "$line" ]]; do
      line="${line%$'\r'}"
      if [[ "$line" == "$key="* ]]; then
        value="${line#*=}"
        found=1
      fi
    done < "$file"
  done
  [[ $found -eq 1 ]] || return 1

  if [[ ${#value} -ge 2 ]]; then
    if [[ "${value:0:1}" == '"' && "${value: -1}" == '"' ]]; then
      value="${value:1:${#value}-2}"
    elif [[ "${value:0:1}" == "'" && "${value: -1}" == "'" ]]; then
      value="${value:1:${#value}-2}"
    fi
  fi
  printf '%s' "$value"
}

configure_target() {
  local choice configured_url
  local -a config_files

  bold "Canery administration"
  printf '  1) Canery production (default)\n'
  printf '  2) Docker development\n'
  printf '  3) Local API\n'
  printf '  4) Custom URL\n'
  prompt choice "Target" "1"

  case "${choice,,}" in
    1|canery|production|prod)
      target_name="Canery"
      api_base="$canery_api_default"
      config_files=(.env)
      ;;
    2|dev|development)
      target_name="development"
      api_base="$dev_api_default"
      config_files=(.env .env.dev)
      ;;
    3|local)
      target_name="local"
      api_base="$local_api_default"
      config_files=(.env)
      ;;
    4|custom)
      target_name="custom"
      prompt api_base "API base URL (for example https://api.example.com)"
      config_files=(.env)
      ;;
    *)
      fail "unknown target: $choice"
      ;;
  esac

  configured_url="${BLOG_ADMIN_API_URL:-}"
  api_base="${configured_url:-$api_base}"
  api_base="${api_base%/}"
  [[ "$api_base" =~ ^https?://[^[:space:]]+$ ]] || fail "API URL must be absolute http(s)"

  admin_prefix="${BLOG_ADMIN_PATH_PREFIX:-${BLOGS_ADMIN_PATH_PREFIX:-}}"
  if [[ -z "$admin_prefix" ]]; then
    admin_prefix="$(dotenv_value BLOGS_ADMIN_PATH_PREFIX "${config_files[@]}" || true)"
  fi
  if [[ -z "$admin_prefix" ]]; then
    prompt_secret admin_prefix "Secret admin route prefix"
  fi
  [[ -n "$admin_prefix" ]] || fail "admin route prefix is required"
  admin_prefix="/${admin_prefix#/}"
  admin_prefix="${admin_prefix%/}"
  [[ "$admin_prefix" =~ ^/[A-Za-z0-9._~/-]+$ ]] || \
    fail "admin route prefix contains unsupported characters"
  admin_root="$api_base$admin_prefix/admin"

  admin_email="${BLOG_ADMIN_EMAIL:-${BLOGS_ADMIN_EMAIL:-}}"
  if [[ -z "$admin_email" ]]; then
    admin_email="$(dotenv_value BLOGS_ADMIN_EMAIL "${config_files[@]}" || true)"
  fi
  admin_password="${BLOG_ADMIN_PASSWORD:-}"
  access_token="${BLOG_ADMIN_ACCESS_TOKEN:-}"

  info "Target: $target_name ($api_base)"
}

write_auth_config() {
  [[ "$access_token" =~ ^[A-Za-z0-9._~-]+$ ]] || fail "API returned a malformed access token"
  umask 077
  printf 'header = "Authorization: Bearer %s"\n' "$access_token" > "$auth_config"
  chmod 600 "$auth_config"
}

show_api_error() {
  if jq -e '.error.safe_message? // empty' "$response_file" >/dev/null 2>&1; then
    jq -r '"\(.error.category): \(.error.safe_message)"' "$response_file" >&2
    jq -r 'select(.error.correlation_id? != null) | "Correlation: \(.error.correlation_id)"' \
      "$response_file" >&2
  elif jq -e '.message? // empty' "$response_file" >/dev/null 2>&1; then
    jq -r '.message' "$response_file" >&2
  else
    printf 'HTTP %s returned an unexpected response.\n' "$last_http_status" >&2
    sed -n '1,20p' "$response_file" >&2
  fi
}

show_api_success() {
  jq -r '.message // "Done."' "$response_file"
  jq '.data' "$response_file"
}

public_json_request() {
  local method="$1"
  local url="$2"
  local payload="${3:-}"

  if [[ -n "$payload" ]]; then
    if ! last_http_status="$(
      printf '%s' "$payload" | curl --silent --show-error \
        --proto '=http,https' --connect-timeout 10 --max-time 60 \
        --request "$method" --header 'Content-Type: application/json' \
        --data-binary @- --output "$response_file" --write-out '%{http_code}' "$url"
    )"; then
      warn "could not reach $api_base"
      return 1
    fi
  elif ! last_http_status="$(
    curl --silent --show-error --proto '=http,https' --connect-timeout 10 --max-time 60 \
      --request "$method" \
      --output "$response_file" --write-out '%{http_code}' "$url"
  )"; then
    warn "could not reach $api_base"
    return 1
  fi

  [[ "$last_http_status" =~ ^2[0-9][0-9]$ ]]
}

admin_login() {
  local login_payload

  if [[ -z "$admin_email" ]]; then
    prompt admin_email "Admin email"
  else
    info "Admin email: $admin_email"
  fi
  if [[ -z "$admin_password" ]]; then
    prompt_secret admin_password "Admin password"
  fi
  [[ -n "$admin_email" && -n "$admin_password" ]] || {
    warn "email and password are required"
    return 1
  }

  login_payload="$(jq -cn \
    --arg email "$admin_email" \
    --arg password "$admin_password" \
    '{email: $email, password: $password}')"
  if ! public_json_request POST "$api_base$admin_prefix/auth/login" "$login_payload"; then
    show_api_error
    access_token=""
    return 1
  fi
  access_token="$(jq -r '.data.access_token // empty' "$response_file")"
  [[ -n "$access_token" ]] || {
    warn "login succeeded without an access token"
    return 1
  }
  write_auth_config
  info "Admin session ready."
}

authenticated_json_raw() {
  local method="$1"
  local url="$2"
  local payload="${3:-}"

  if [[ -n "$payload" ]]; then
    last_http_status="$(
      printf '%s' "$payload" | curl --silent --show-error \
        --proto '=http,https' --connect-timeout 10 --max-time 60 \
        --config "$auth_config" --request "$method" \
        --header 'Content-Type: application/json' --data-binary @- \
        --output "$response_file" --write-out '%{http_code}' "$url"
    )"
  else
    last_http_status="$(curl --silent --show-error \
      --proto '=http,https' --connect-timeout 10 --max-time 60 \
      --config "$auth_config" --request "$method" \
      --output "$response_file" --write-out '%{http_code}' "$url")"
  fi
}

authenticated_json_request() {
  local method="$1"
  local url="$2"
  local payload="${3:-}"

  if ! authenticated_json_raw "$method" "$url" "$payload"; then
    warn "could not reach $api_base"
    return 1
  fi
  if [[ "$last_http_status" == "401" ]]; then
    warn "admin session expired; signing in again"
    access_token=""
    admin_password=""
    admin_login || return 1
    authenticated_json_raw "$method" "$url" "$payload" || {
      warn "could not reach $api_base"
      return 1
    }
  fi
  if [[ ! "$last_http_status" =~ ^2[0-9][0-9]$ ]]; then
    show_api_error
    return 1
  fi
  return 0
}

authenticated_form_request() {
  local url="$1"
  shift

  if ! last_http_status="$(curl --silent --show-error \
    --proto '=http,https' --connect-timeout 10 --max-time 120 \
    --config "$auth_config" --request POST "$@" \
    --output "$response_file" --write-out '%{http_code}' "$url")"; then
    warn "could not reach $api_base"
    return 1
  fi
  if [[ "$last_http_status" == "401" ]]; then
    warn "admin session expired; signing in again"
    access_token=""
    admin_password=""
    admin_login || return 1
    if ! last_http_status="$(curl --silent --show-error \
      --proto '=http,https' --connect-timeout 10 --max-time 120 \
      --config "$auth_config" --request POST "$@" \
      --output "$response_file" --write-out '%{http_code}' "$url")"; then
      warn "could not reach $api_base"
      return 1
    fi
  fi
  if [[ ! "$last_http_status" =~ ^2[0-9][0-9]$ ]]; then
    show_api_error
    return 1
  fi
  return 0
}

ensure_admin_session() {
  if [[ -n "$access_token" ]]; then
    write_auth_config
    if authenticated_json_raw GET "$api_base$admin_prefix/session" &&
      [[ "$last_http_status" =~ ^2[0-9][0-9]$ ]]; then
      info "Existing admin token accepted."
      return 0
    fi
    warn "the supplied admin token was not accepted; using password sign-in"
    access_token=""
  fi
  admin_login
}

append_form_value() {
  local array_name="$1"
  local field="$2"
  local value="$3"
  [[ -n "$value" ]] || return 0
  local -n form_array="$array_name"
  form_array+=(--form-string "$field=$value")
}

publish_blog() {
  local file_path status use_overrides
  local title summary slug categories series series_position
  local cover_image_url cover_image_alt tags tier difficulty prerequisites
  local canonical_url published_on content_updated_on
  local -a form_args

  bold "Publish a blog"
  prompt file_path "Markdown file"
  if [[ "$file_path" == '~/'* ]]; then
    file_path="${HOME}/${file_path:2}"
  fi
  [[ -f "$file_path" ]] || { warn "file does not exist: $file_path"; return 1; }

  prompt status "Status (published/draft)" "published"
  case "$status" in
    published|draft) ;;
    *) warn "status must be published or draft"; return 1 ;;
  esac

  prompt use_overrides "Override Markdown frontmatter fields? (y/N)" "N"
  title=""; summary=""; slug=""; categories=""; series=""; series_position=""
  cover_image_url=""; cover_image_alt=""; tags=""; tier=""; difficulty=""
  prerequisites=""; canonical_url=""; published_on=""; content_updated_on=""

  if [[ "${use_overrides,,}" == "y" || "${use_overrides,,}" == "yes" ]]; then
    info "Leave any value empty to keep the Markdown frontmatter value."
    prompt title "Title"
    prompt summary "Summary/description"
    prompt slug "Slug"
    prompt categories "Category keys (comma-separated)"
    prompt series "Series key"
    prompt series_position "Series position (0 or greater)"
    prompt cover_image_url "Cover image URL"
    if [[ -n "$cover_image_url" ]]; then
      prompt cover_image_alt "Cover image alt text"
      [[ -n "$cover_image_alt" ]] || { warn "cover alt text is required with a cover URL"; return 1; }
    fi
    prompt tags "Tag keys (comma-separated)"
    prompt tier "Tier (L1/L2/L3/L4)"
    if [[ -n "$tier" && ! "$tier" =~ ^L[1-4]$ ]]; then
      warn "tier must be L1, L2, L3, or L4"
      return 1
    fi
    prompt difficulty "Difficulty (beginner/intermediate/advanced)"
    if [[ -n "$difficulty" && ! "$difficulty" =~ ^(beginner|intermediate|advanced)$ ]]; then
      warn "difficulty must be beginner, intermediate, or advanced"
      return 1
    fi
    prompt prerequisites "Prerequisites (comma-separated)"
    prompt canonical_url "Canonical URL"
    prompt published_on "Editorial publish date (YYYY-MM-DD)"
    prompt content_updated_on "Editorial update date (YYYY-MM-DD)"
  fi

  form_args=(--form "file=@${file_path};type=text/markdown")
  append_form_value form_args status "$status"
  append_form_value form_args title "$title"
  append_form_value form_args summary "$summary"
  append_form_value form_args slug "$slug"
  append_form_value form_args categories "$categories"
  append_form_value form_args series "$series"
  append_form_value form_args series_position "$series_position"
  append_form_value form_args cover_image_url "$cover_image_url"
  append_form_value form_args cover_image_alt "$cover_image_alt"
  append_form_value form_args tags "$tags"
  append_form_value form_args tier "$tier"
  append_form_value form_args difficulty "$difficulty"
  append_form_value form_args prerequisites "$prerequisites"
  append_form_value form_args canonical_url "$canonical_url"
  append_form_value form_args published_on "$published_on"
  append_form_value form_args content_updated_on "$content_updated_on"

  authenticated_form_request "$admin_root/blogs" "${form_args[@]}" || return 1
  show_api_success
}

upsert_category() {
  local key label description payload
  bold "Create or update a category"
  prompt key "Key (lowercase-hyphenated)"
  prompt label "Label"
  prompt description "Description (optional)"
  [[ -n "$key" && -n "$label" ]] || { warn "key and label are required"; return 1; }
  payload="$(jq -cn --arg key "$key" --arg label "$label" --arg description "$description" \
    '{key: $key, label: $label, description: (if $description == "" then null else $description end)}')"
  authenticated_json_request PUT "$admin_root/categories" "$payload" || return 1
  show_api_success
}

upsert_series() {
  local key title description payload
  bold "Create or update a series"
  prompt key "Key (lowercase-hyphenated)"
  prompt title "Title"
  prompt description "Description (optional)"
  [[ -n "$key" && -n "$title" ]] || { warn "key and title are required"; return 1; }
  payload="$(jq -cn --arg key "$key" --arg title "$title" --arg description "$description" \
    '{key: $key, title: $title, description: (if $description == "" then null else $description end)}')"
  authenticated_json_request PUT "$admin_root/series" "$payload" || return 1
  show_api_success
}

list_blogs() {
  local status
  prompt status "Status (published/draft/archived)" "published"
  case "$status" in
    published|draft|archived) ;;
    *) warn "unknown status: $status"; return 1 ;;
  esac
  authenticated_json_request GET "$admin_root/blogs?status=$status&limit=100" || return 1
  printf '%-38s  %-10s  %-28s  %s\n' "ID" "STATUS" "SLUG" "TITLE"
  jq -r '.data.items[] | [.id, .status, .slug, .title] | @tsv' "$response_file" |
    while IFS=$'\t' read -r id item_status slug title; do
      printf '%-38s  %-10s  %-28s  %s\n' "$id" "$item_status" "$slug" "$title"
    done
}

list_categories() {
  public_json_request GET "$api_base/api/v1/categories" || { show_api_error; return 1; }
  printf '%-28s  %-28s  %s\n' "KEY" "LABEL" "DESCRIPTION"
  jq -r '.data[] | [.key, .label, (.description // "")] | @tsv' "$response_file" |
    while IFS=$'\t' read -r key label description; do
      printf '%-28s  %-28s  %s\n' "$key" "$label" "$description"
    done
}

list_series() {
  public_json_request GET "$api_base/api/v1/series" || { show_api_error; return 1; }
  printf '%-38s  %-28s  %-28s  %s\n' "ID" "KEY" "TITLE" "DESCRIPTION"
  jq -r '.data[] | [.id, .key, .title, (.description // "")] | @tsv' "$response_file" |
    while IFS=$'\t' read -r id key title description; do
      printf '%-38s  %-28s  %-28s  %s\n' "$id" "$key" "$title" "$description"
    done
}

list_resources() {
  local choice
  bold "List resources"
  printf '  1) Blogs\n  2) Categories\n  3) Series\n'
  prompt choice "Resource" "1"
  case "$choice" in
    1) list_blogs ;;
    2) list_categories ;;
    3) list_series ;;
    *) warn "unknown resource"; return 1 ;;
  esac
}

delete_resource() {
  local choice identifier encoded
  bold "Archive or delete"
  printf '  1) Archive blog\n'
  printf '  2) Delete category\n'
  printf '  3) Delete series\n'
  prompt choice "Resource" "1"

  case "$choice" in
    1)
      prompt identifier "Blog UUID"
      [[ -n "$identifier" ]] || { warn "blog UUID is required"; return 1; }
      confirm_exact "$identifier" \
        "This archives the blog; reader history is preserved." || { info "Cancelled."; return 0; }
      authenticated_json_request DELETE "$admin_root/blogs/$identifier" || return 1
      ;;
    2)
      prompt identifier "Category key"
      [[ -n "$identifier" ]] || { warn "category key is required"; return 1; }
      confirm_exact "$identifier" \
        "The category can only be deleted when no article uses it." || { info "Cancelled."; return 0; }
      encoded="$(jq -rn --arg value "$identifier" '$value | @uri')"
      authenticated_json_request DELETE "$admin_root/categories/$encoded" || return 1
      ;;
    3)
      prompt identifier "Series key"
      [[ -n "$identifier" ]] || { warn "series key is required"; return 1; }
      confirm_exact "$identifier" \
        "Deleting this series keeps its blogs but removes their series assignment." || \
        { info "Cancelled."; return 0; }
      encoded="$(jq -rn --arg value "$identifier" '$value | @uri')"
      authenticated_json_request DELETE "$admin_root/series/$encoded" || return 1
      ;;
    *)
      warn "unknown resource"
      return 1
      ;;
  esac
  show_api_success
}

main_menu() {
  local choice
  while true; do
    bold "What would you like to do?"
    printf '  1) Publish blog\n'
    printf '  2) Add/update category\n'
    printf '  3) Add/update series\n'
    printf '  4) List resources\n'
    printf '  5) Archive/delete resource\n'
    printf '  0) Exit\n'
    prompt choice "Action" "1"

    case "$choice" in
      1) publish_blog || true ;;
      2) upsert_category || true ;;
      3) upsert_series || true ;;
      4) list_resources || true ;;
      5) delete_resource || true ;;
      0|q|quit|exit) info "Bye."; return 0 ;;
      *) warn "unknown action: $choice" ;;
    esac
  done
}

configure_target
ensure_admin_session || fail "admin sign-in failed"
main_menu
