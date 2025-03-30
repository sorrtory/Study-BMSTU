#!/bin/bash
export LOGXI=*
export LOGXI_FORMAT=pretty,happy
MyIP=$(hostname -I | awk '{ print $1 }' | tr -d '[:space:]')
export MyIP
echo "Building..."
go build -o fedukov_lab3
echo "Running..."
./fedukov_lab3
