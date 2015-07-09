#!/bin/bash
# run this script with root
# $1 <Weave internal IP with mask>
# $2 <hostname files with all agents>

if [ $# -lt 2 ]; then
    echo "usage: ./sever_setup.sh <Weave internal IP with mask> <hostname file with all agents>"
    echo "example: ./server_setup.sh 192.168.10.10/16 /user/simulator-script/hosts.txt"
    echo "note: the hostname file is generated automatically when you request a cluster"
    exit 1
fi

# install weave
chmod 755 ./Linux/CentOS7/weave_install.sh
./Linux/CentOS7/weave_install.sh

# reset weave
weave reset

# launch weave
weave launch

# expose IP
weave expose $1

# add hosname of all agents
cat $2 >> /etc/hosts3