echo "Hope RosBE and ReactOS paths are alright"

s=$(pwd)
#source env.txt
cd ../ReactOS/RosBE-Unix-2.2.1/bin/
source RosBE2.sh
cd $s


echo "Clean up"
cd ./reactos-master/
clean
./configure.sh
cd output-MinGW-i386/
echo "Start the compilation"
ninja lab3

rm -i ../../SharedDrive/lab3.sys
if [ ! -e ../../SharedDrive/lab3.sys ]; then
    cp drivers/lab3/lab3.sys ../../SharedDrive
    cd ../../
    genisoimage -o shared_lab3.iso SharedDrive/
fi
