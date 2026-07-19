#!/usr/bin/env bash

# This script creates a new labN directory with the appropriate file structure

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

## Numberic methods course structure

# create task directory
mkdir task

# create solution directory
mkdir solution
mkdir .oldversions
touch solution/main.py

# create report
cp -r ../lab1/report report
sed -i "s/Лабораторная работа № 1/Лабораторная работа № ${LAB_NUMBER}/" report/TitlePages/titlepage-lab.tex
sed -i "s/Решение СЛАУ c 3-x диагональной матрицей методом прогонки//" report/TitlePages/titlepage-lab.tex

# create symbolic link
rm report/Listings/main.py
~/Documents/scripts/link.sh "solution/main.py" "report/Listings/main.py"
~/Documents/scripts/link.sh "report/main.pdf" "main.pdf"
# use: cp -L main.pdf Fedukov_labN.pdf
touch Fedukov_lab${LAB_NUMBER}.pdf