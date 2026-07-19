#!/bin/sh
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
formatter="$root/basic-formatter"

check_format() {
    name=$1
    "$formatter" "$root/tests/$name.bas" > "$root/tests/$name.actual"
    diff -u "$root/tests/$name.expected" "$root/tests/$name.actual"
}

check_format example
check_format do-loops

echo "All tests passed"
