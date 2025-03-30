#!/bin/bash
export LOGXI=*
export LOGXI_FORMAT=pretty,happy
go build -o fedukov_lab2
echo "Running..."
kill $(pgrep fedukov_lab2) > /dev/null 2>&1
./fedukov_lab2
