#!/bin/bash
export LOGXI=*
export LOGXI_FORMAT=pretty,happy
MyIP=$(hostname -I | awk '{ print $1 }' | tr -d '[:space:]')
export MyIP
echo "Building..."
if [[ -e fedukov_lab3 ]]; then
    rm fedukov_lab3
fi
go build -o fedukov_lab3
echo "Running..."
kill $(pgrep fedukov_lab3) > /dev/null 2>&1
./fedukov_lab3
