#!/bin/bash
# Scipt that uploads files of lab and launches them on ssh hosts
# Requirements: "tmux" to control ssh, existing ssh-keys or "sshpass" to generate keys
# IHAVESSHKEY=false to generate keys

SESSION="MySSH"
tmux kill-session -t $SESSION
tmux new-session -d -s $SESSION

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd ) # Lab files dir. Default is script's dir
src=("$SCRIPT_DIR/ftp/*.go") # Files to upload
path=/root/Fedukov/lab7/ # Path to lab folder on server
startCommand="go mod init main; go mod tidy; go run ." # Launch command 
NetworkList=("yss1") # List of ssh hosts (supposed to use ssh key)

# Options
clearMode=false # Remove lab dirs and exit
forceClear=true # Don't ask for confirmation before replacing lab files
justStart=false # Don't upload files, just execute $startCommand on server in tmux
IHAVESSHKEY=true # Set false and set IPS and PASSWORDS to generate ssh keys

# Read IPs and passwords into arrays
IPS=("185.104.251.226" "185.102.139.161" "185.102.139.168" "185.102.139.169")
PASSWORDS=("fMs0m69gIGQ3" "Up5b0A1wiLMQ" "gOsQ5p7FUJ9w" "w3Bt8hjge8oV")

function generateSSHKeys {

    # SSH configuration file
    SSH_CONFIG="$HOME/.ssh/config"
    SSH_KEY="$HOME/.ssh/id_rsa_for_lab"

    # Function to check if host is already in SSH config
    function host_in_ssh_config() {
        local host="$1"
        if grep -q "Host $host" "$SSH_CONFIG"; then
            return 0  # Found
        else
            return 1  # Not found
        fi
    }

    # Check if SSH keys exist, generate if not
    if [ ! -f "$SSH_KEY" ]; then
        echo "Generating SSH key..."
        ssh-keygen -t rsa -b 4096 -N "" -f "$SSH_KEY"
    fi

    # Make sure both lists have the same length
    if [ "${#IPS[@]}" -ne "${#PASSWORDS[@]}" ]; then
        echo "Error: IP list and password list must have the same number of entries."
        exit 1
    fi

    useIpsAsHostNames=false
    if [ "${#IPS[@]}" -ne "${#NetworkList[@]}" ]; then
        echo "Not enough names in NetworkList. Using ip as a name"
        useIpsAsHostNames=true
    fi

    # Backup existing SSH config file
    if [ -f "$SSH_CONFIG" ]; then
        local i=1

        while [ -f "${SSH_CONFIG}.bak.$i" ]; do
            i=$((i + 1))
        done

        cp "$SSH_CONFIG" "${SSH_CONFIG}.bak.$i"
        echo "Backup of SSH config created at ${SSH_CONFIG}.bak.$i"        
    fi

    # Create SSH config entries or skip if already exists
    for i in "${!IPS[@]}"; do
        IP="${IPS[$i]}"
        PASSWORD="${PASSWORDS[$i]}"
        if [ $useIpsAsHostNames = true ]; then
            HOST=$IP
        else
            HOST="${NetworkList[$i]}"
        fi

        if host_in_ssh_config "$HOST"; then
            echo "Host $HOST is already in SSH config, skipping..."
            continue
        fi

        echo "Setting up passwordless SSH for $HOST ($IP)..."

        # Copy SSH key to remote server using sshpass
        sshpass -p "$PASSWORD" ssh-copy-id -i "$SSH_KEY.pub" "root@$IP"

        # Add SSH config entry
        echo "Host $HOST" >> "$SSH_CONFIG"
        echo "  HostName $IP" >> "$SSH_CONFIG"
        echo "  User root" >> "$SSH_CONFIG"
        echo "  IdentityFile $SSH_KEY" >> "$SSH_CONFIG"
        echo "  IdentitiesOnly yes" >> "$SSH_CONFIG"
        echo "  StrictHostKeyChecking no" >> "$SSH_CONFIG"      # It causes "Warning: Permanently added"
        echo "  UserKnownHostsFile /dev/null" >> "$SSH_CONFIG"  # Don't write to known hosts
    done

    echo "SSH configuration updated at $SSH_CONFIG"
}

if [ $IHAVESSHKEY = false ]; then
    generateSSHKeys
fi

function addTmuxWindow {
    i=$1 # Vps id
    vps=$2 # Vps name
    path=$3 # Lab dir path

    # Launch program in tmux via ssh
    tmux new-window -t $SESSION:$((i + 1)) -n ${NetworkList[i]} ssh $vps "cd $path; source ~/.profile; $startCommand"
    
    echo "Tmux windows created"
}

function isDirEmpty {
    vps=$1
    path=$2
    [ $(ssh $vps "ls -1 $path | wc -l") -eq "0" ]
}

function doesDirExist {
    vps=$1
    path=$2
    ssh $vps "[ -e $path ]"
}

function removeDir {
    vps=$1
    path=$2

    if [ $forceClear = false ]; then
        echo "Clean folder?"
        echo "ls -a $path"
        echo "----"
        ssh $vps "ls -a $path"
        echo "----"
        select yn in "Yes" "No"; do
            case $yn in
                Yes) break;;
                No) echo "Skip"; return;;
            esac
        done

    fi

    ssh $vps "rm -rf $path/*"
    echo "Cleaned folder"
}

# Check src files existence
for file in ${src[*]}
do
    if [ ! -e $file ]; then
        echo -e "\nFile not found: $file\n" 
    fi
done


for i in ${!NetworkList[*]}
do
    echo "Processing on ${NetworkList[i]} ..."
    vps=${NetworkList[i]}

    if [ $clearMode = true ]; then 
        removeDir $vps $path
    else

        if ! doesDirExist $vps $path; then
            echo "$path not found"
            ssh $vps "mkdir -p $path"
            echo "Created $path"
        fi

        if [ $justStart = true ]; then
            if ! isDirEmpty $vps $path; then
                addTmuxWindow $i $vps $path
            else
                echo "No files to start. Skip"
            fi
        else
            removeDir $vps $path
            echo "Loading files"
            scp -r ${src[*]} $vps:$path
            
            addTmuxWindow $i $vps $path
        fi
    fi
done

if [ "$clearMode" = false ]; then
    echo "Starting tmux"
    # Launch tmux in gnome-terminal
    gnome-terminal -- tmux attach -t $SESSION
else 
    echo "Killing tmux"
    tmux kill-session -t $SESSION
fi