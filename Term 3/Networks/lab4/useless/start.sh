#!/bin/bash

MyIP=$(hostname -I | awk '{ print $1 }' | tr -d '[:space:]')
export MyIP

echo "Building..."
# SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd ) # Lab files dir. Default is script's dir
# go mod init main
# go get github.com/PuerkitoBio/goquery@v1.9.3
# go get github.com/cavaliergopher/grab/v3
# go mod tidy
go build -o fedukov_lab4
echo "Running..."
killall fedukov_lab4
./fedukov_lab4
