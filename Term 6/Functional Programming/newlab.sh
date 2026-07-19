#!/usr/bin/env bash

# This script creates a new labN directory with the appropriate file structure
cd labs

LAB_NUMBER=$1

if [ -z "$LAB_NUMBER" ]; then
    # Find the latest lab number
    latest_num=$(ls -d lab[0-9]* 2>/dev/null | sed 's/lab//' | sort -n | tail -1)
    if [ -z "$latest_num" ]; then
        LAB_NUMBER=1
    else
        LAB_NUMBER=$((latest_num + 1))
    fi
fi

# Check if the lab number is provided and is a valid number
if [ -z "$LAB_NUMBER" ] || ! [[ $LAB_NUMBER =~ ^[0-9]+$ ]]; then
    echo "Usage: $0 <lab-number>"
    exit 1
fi

LAB_DIR="lab${LAB_NUMBER}"

if [ -d "$LAB_DIR" ]; then
    echo "Directory $LAB_DIR already exists. Please choose a different lab number."
    exit 1
fi

mkdir "$LAB_DIR"
cd "$LAB_DIR"

## Functional programming course structure

# create report
touch report.md

# Create readme
touch README.md
echo "# Lab ${LAB_NUMBER}" > README.md

# create task directory
mkdir task

# create src directory
mkdir src