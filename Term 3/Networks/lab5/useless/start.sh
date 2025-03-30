#!/bin/bash

MyIP=$(hostname -I | awk '{ print $1 }' | tr -d '[:space:]')
export MyIP

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd ) # Lab files dir. Default is script's dir
cd "$SCRIPT_DIR" || exit 1

echo "Building..."
cd main || exit 1
rm go.mod go.sum
go mod init main
# Import
# go get "github.com/SlyMarbo/rss"
# go get "github.com/gorilla/websocket"
# go get github.com/go-sql-driver/mysql
go mod tidy

go build -o ../fedukov_lab5
killall fedukov_lab5 2>/dev/null
echo "Running..."
../fedukov_lab5
