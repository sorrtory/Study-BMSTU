#!/bin/bash

SESSION="MySSH"
# tmux attach -t MySSH
tmux kill-session -t $SESSION
tmux new-session -d -s $SESSION

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
src=($SCRIPT_DIR/client.go $SCRIPT_DIR/server.go $SCRIPT_DIR/socketServer.go  $SCRIPT_DIR/main.go $SCRIPT_DIR/start.sh)
path=/root/Fedukov/lab3
NetworkList=("yss1" "yss2" "yss3" "yss4")
forceClear=true # Don't confirm for replacing lab3 files
clearMode=false # Just remove lab3 files
for i in ${!NetworkList[*]}
do
    echo "Go for ${NetworkList[i]} ..."
    vps=${NetworkList[i]}
    if ssh $vps "[ -e $path ]"; then
        if [ ! $(ssh $vps "ls -1 $path | wc -l") -eq "0" ]; then
            if [ "$forceClear" = true ] || [ "$clearMode" = true ]; then
                echo "Clean folder"
                ssh $vps "rm -f $path/*"
            else
                echo "Clear folder?"
                select yn in "Yes" "No"; do
                    case $yn in
                        Yes) ssh $vps "rm -f $path/*"; break;;
                        No) echo "Exit"; exit;;
                    esac
                done
            fi
        fi
    else
        echo "No such dir. Creating "
        ssh $vps "mkdir -p $path"
    fi
    
    if [ "$clearMode" = false ]; then
        echo "Load files"
        scp ${src[*]} $vps:$path
        ssh $vps "kill \$(pgrep fedukov_lab3) > /dev/null 2>&1; cd $path; source ~/.profile;  go mod init main; go mod tidy > /dev/null 2>&1;"
        # echo -n "Process started on server by PID: "
        # ssh $vps "cd $path; source ~/.profile; sh -c '(( nohup ./start.sh > /dev/null 2>&1 & ))'"
        # ssh $vps "echo \$(pgrep fedukov_lab3)"

        tmux new-window -t $SESSION:$((i + 1)) -n ${NetworkList[i]} ssh $vps "cd $path; source ~/.profile; ./start.sh"
    fi
done

if [ "$clearMode" = false ]; then
    gnome-terminal -- tmux attach -t $SESSION
else 
    tmux kill-session -t $SESSION
fi