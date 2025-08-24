echo "Hope RosBE and ReactOS paths are alright"

#s=$(pwd)
#source env.txt
#cd ../ReactOS/RosBE-Unix-2.2.1/bin/
#source RosBE2.sh
#cd $s


#echo "Clean up"
#cd ./reactos-master/
#clean
#./configure.sh
#cd output-MinGW-i386/
#echo "Start the compilation"
#ninja lab4

rm -i SharedDrive/lab4.sys
if [ ! -e SharedDrive/lab4.sys ]; then
    cp ./reactos-master/output-MinGW-i386/drivers/lab4/lab4.sys SharedDrive/
    genisoimage -o shared_lab4.iso SharedDrive/
fi
