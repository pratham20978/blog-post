#!/usr/bin/env bash
set -euo pipefail

MODEL_NAME="${MODEL_NAME:-TinyLlama-1.1B-Chat-v1.0}"
TOKENIZER_ID="${TOKENIZER_ID:-TinyLlama/TinyLlama-1.1B-Chat-v1.0}"
RESULT_DIR="${RESULT_DIR:-benchmark-results}"
REQUEST_COUNT="${REQUEST_COUNT:-100}"
REQUEST_RATE="${REQUEST_RATE:-10}"
INPUT_TOKENS="${INPUT_TOKENS:-128}"
OUTPUT_TOKENS="${OUTPUT_TOKENS:-128}"
SERVER_URL="${SERVER_URL:-localhost:8000}"

command -v aiperf >/dev/null 2>&1 || {
    printf 'aiperf is not installed in this environment\n' >&2
    exit 2
}

mkdir -p "$RESULT_DIR"

aiperf profile \
    -m "$MODEL_NAME" \
    --tokenizer "$TOKENIZER_ID" \
    --endpoint-type chat \
    --random-seed 123 \
    --synthetic-input-tokens-mean "$INPUT_TOKENS" \
    --synthetic-input-tokens-stddev 0 \
    --output-tokens-mean "$OUTPUT_TOKENS" \
    --output-tokens-stddev 0 \
    --request-count "$REQUEST_COUNT" \
    --request-rate "$REQUEST_RATE" \
    --profile-export-file "${RESULT_DIR}/profile.json" \
    --url "$SERVER_URL" \
    --streaming
