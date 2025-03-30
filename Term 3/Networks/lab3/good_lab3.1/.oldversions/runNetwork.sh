#!/bin/bash
# Scipt that uploads files of lab and launches them on ssh hosts

SESSION="MySSH"
tmux kill-session -t $SESSION
tmux new-session -d -s $SESSION

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd ) # Lab files dir. Default is script's dir
src=($SCRIPT_DIR/client.go $SCRIPT_DIR/server.go $SCRIPT_DIR/socketServer.go $SCRIPT_DIR/httpServer.go $SCRIPT_DIR/sseServer.go $SCRIPT_DIR/main.go $SCRIPT_DIR/start.sh) # Files to upload
path=/root/Fedukov/lab3 # Path to lab folder on server
startCommand="./start.sh" # Launch command 
NetworkList=("yss1" "yss2" "yss3" "yss4") # List of ssh hosts (suppose using ssh key)

# Options
clearMode=false # Only remove lab files mode
justStart=true # Don't upload files, just launch start.sh on server by tmux
forceClear=true # Don't ask for confirmatin before replacing lab files


function addTmuxWindow {
    i=$1 # Vps id
    # check for existance ...
    tmux new-window -t $SESSION:$((i + 1)) -n ${NetworkList[i]} ssh $vps "cd $path; source ~/.profile; $startCommand"
}

function emptyPathDir {
    [ $(ssh $vps "ls -1 $path | wc -l") -eq "0" ]
}

function existPathDir {
    ssh $vps "[ -e $path ]"
}

for i in ${!NetworkList[*]}
do
    echo "Go for ${NetworkList[i]} ..."
    vps=${NetworkList[i]}
    if ssh $vps "[ -e $path ]"; then
        if [ ! $(ssh $vps "ls -1 $path | wc -l") -eq "0" ]; then
            if [ "$justStart" != true ]; then
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
        fi
    else
        echo "No such dir at the $path "
        if [ "$clearMode" != true ];then 
            echo "Creating"
            ssh $vps "mkdir -p $path"
        fi
    fi
    
    if [ "$clearMode" = false ]; then
        if [ "$justStart" != true ]; then 
            echo "Load files"
            scp ${src[*]} $vps:$path
            ssh $vps "kill \$(pgrep fedukov_lab3) > /dev/null 2>&1; cd $path; source ~/.profile;  go mod init main; go mod tidy > /dev/null 2>&1;"
        fi
        # echo -n "Process started on server by PID: "
        # ssh $vps "cd $path; source ~/.profile; sh -c '(( nohup ./start.sh > /dev/null 2>&1 & ))'"
        # ssh $vps "echo \$(pgrep fedukov_lab3)"
        addTmuxWindow $i
    fi
done

if [ "$clearMode" = false ]; then
    # Tmux launch in gnome-terminal
    gnome-terminal -- tmux attach -t $SESSION
else 
    tmux kill-session -t $SESSION
fi