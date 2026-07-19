#!/bin/sh
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
formatter="$root/basic-formatter"

echo "Running invalid syntax test: tests/invalid.bas"
echo

if "$formatter" "$root/tests/invalid.bas"; then
    echo
    echo "invalid.bas: expected a syntax error, but formatter exited successfully" >&2
    exit 1
fi

echo
echo "Formatter failed as expected"
