#!/usr/bin/env bash
set -euo pipefail

PROM_URL="${PROM_URL:-http://localhost:9090}"
WINDOW="${WINDOW:-30m}"
MODE="${MODE:-increase}"
BY_OPERATION=0

usage() {
  cat <<'EOF'
Usage:
  scripts/compare-latency.sh [--by-operation] [--runs]

Environment filters:
  PROM_URL       Prometheus URL, default: http://localhost:9090
  WINDOW         Prometheus range window, default: 30m
  MODE           increase or rate, default: increase
  RUN_ID         run_id regex filter
  MODEL          model regex filter
  SCENARIO       scenario regex filter
  OPERATION      operation regex filter
  STAGE_CLIENTS  stage_clients regex filter

Examples:
  scripts/compare-latency.sh
  WINDOW=2h scripts/compare-latency.sh
  SCENARIO=balanced scripts/compare-latency.sh
  RUN_ID='.*balanced.*' scripts/compare-latency.sh --by-operation
  scripts/compare-latency.sh --runs
EOF
}

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

add_filter() {
  local label="$1"
  local value="$2"

  if [[ -z "$value" ]]; then
    return
  fi

  if [[ -n "$SELECTOR" ]]; then
    SELECTOR+=","
  fi
  SELECTOR+="${label}=~\"${value}\""
}

prom_query() {
  local query="$1"
  curl -fsS -G "${PROM_URL%/}/api/v1/query" --data-urlencode "query=${query}"
}

print_runs() {
  echo "Available run_id values:"
  curl -fsS -G "${PROM_URL%/}/api/v1/label/run_id/values" \
    --data-urlencode 'match[]=loadgen_operation_duration_seconds_bucket' \
    | jq -r '.data[]? // empty'
}

format_quantile_table() {
  local quantile="$1"
  local group="$2"
  local json="$3"

  echo
  printf 'p%s latency, window=%s, mode=%s\n' "$quantile" "$WINDOW" "$MODE"

  if [[ "$group" == "operation" ]]; then
    echo "$json" | jq -r '
      .data.result
      | sort_by(.metric.model, .metric.operation)
      | (["model", "operation", "seconds", "ms"] | @tsv),
        (.[] | [.metric.model, .metric.operation, (.value[1] | tonumber), ((.value[1] | tonumber) * 1000)] | @tsv)
    ' | column -t
  else
    echo "$json" | jq -r '
      .data.result
      | sort_by(.value[1] | tonumber)
      | (["model", "seconds", "ms"] | @tsv),
        (.[] | [.metric.model, (.value[1] | tonumber), ((.value[1] | tonumber) * 1000)] | @tsv)
    ' | column -t
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --by-operation)
      BY_OPERATION=1
      shift
      ;;
    --runs)
      require curl
      require jq
      print_runs
      exit 0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

require curl
require jq
require column

SELECTOR=""
add_filter "run_id" "${RUN_ID:-}"
add_filter "model" "${MODEL:-}"
add_filter "scenario" "${SCENARIO:-}"
add_filter "operation" "${OPERATION:-}"
add_filter "stage_clients" "${STAGE_CLIENTS:-}"

case "$MODE" in
  increase)
    RANGE_EXPR="increase(loadgen_operation_duration_seconds_bucket{${SELECTOR}}[${WINDOW}])"
    ;;
  rate)
    RANGE_EXPR="rate(loadgen_operation_duration_seconds_bucket{${SELECTOR}}[${WINDOW}])"
    ;;
  *)
    echo "MODE must be 'increase' or 'rate', got: $MODE" >&2
    exit 1
    ;;
esac

if [[ "$BY_OPERATION" -eq 1 ]]; then
  GROUPING="le, model, operation"
  GROUP="operation"
else
  GROUPING="le, model"
  GROUP="model"
fi

for q in 0.50 0.95 0.99; do
  query="histogram_quantile(${q}, sum by (${GROUPING}) (${RANGE_EXPR}))"
  json="$(prom_query "$query")"
  format_quantile_table "${q#0.}" "$GROUP" "$json"
done
