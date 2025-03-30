#!/bin/bash

# file_path=$1
# launch_range=$2

time_start=$(date +%s)

ERR_FILE="file_$1.err"
OUT_FILE="file_$1.out"


if [ "$1" = "-e" ]; then
        echo "./1.sh long.py 3 2"
        exit 0
fi

if [ "$1" = "-e" ]; then
	echo "./1.sh long.py 3 2"
	exit 0
fi

if [ ! -f $1 ]; then
	echo "Ошибка, должен быть передан путь к программе!" >&2
       	exit 1
fi

REGEX="^[0-9]+$"
if [[ ! $2 =~ $REGEX ]]; then 
	echo "Ошибка, параметр t это число!" >&2
       	exit 1
fi

function launched {
	if ps aux | grep $1 | grep -v grep | grep -v $0 >/dev/null; then
		return 1
	else 
		return 0	
	fi
}

echo -n  > $OUT_FILE
echo -n  > $ERR_FILE

while true; do
	echo "Попытка запуска $1"	
	if launched $@; then
		./$1 $3 1>>$OUT_FILE 2>>$ERR_FILE &
		echo "Успешный запуск"
		sleep $2
	
	else
		echo "Ошибка, файл уже запущен!" >&2
		exit 1
	fi
done










# (($(date +%s) - time_start)) % launch_range -eq 0



#if [ "$timeout" -eq "0" ]; then
#	python3  $file_path 2>./$ERR_FILE 1>$OUT_FILE 
#fi
