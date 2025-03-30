#!/bin/bash

if [ "$1" = "-e" ]; then
	echo "./2.sh /home/z/algs_fan/"
	exit 0
fi
if [ "$1" = "" ] || [ ! -d $1 ]; then
	echo "Ошибка, необходимо указать путь к директории!"
	exit 1
fi

function go {
	sum=0
	for i in $(ls $1); do
		if [ -d $1$i ]; then
			(( sum = $sum + $(go "$1$i/") ))		
		fi

		if [[ $i =~ \.[ch]$ ]]; then
			(( sum = $sum + $(grep -c "\S" $1$i) ))
		fi
	done

	echo $sum
}

go $1


