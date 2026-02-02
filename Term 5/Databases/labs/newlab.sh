#!/bin/bash
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <number>"
    exit 1
fi

arg="$1"
if ! [[ "$arg" =~ ^[0-9]+$ ]]; then
    echo "Error: argument must be a number"
    exit 2
fi

dir="lab${arg}"
sqlfile="${dir}.sql"
sqlpath="${dir}/${sqlfile}"

# create directory if missing
if [ -d "$dir" ]; then
    echo "Directory '$dir' exists"
else
    mkdir -p -- "$dir" || { echo "Failed to create directory '$dir'"; exit 3; }
    echo "Created directory '$dir'"
fi

# create sql file inside the directory if missing
if [ -e "$sqlpath" ]; then
    echo "SQL file '$sqlpath' exists"
else
    : > "$sqlpath" || { echo "Failed to create SQL file '$sqlpath'"; exit 4; }
    chmod 644 "$sqlpath"
    echo "Created SQL file '$sqlpath'"
fi