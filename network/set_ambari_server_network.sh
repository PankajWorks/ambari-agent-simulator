#!/bin/bash
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information rega4rding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script will configure the ambari-server
# including, set Weave network and add agent hostname resolution

# run this script with root
# $1 <Weave internal IP with mask>
# $2 <hostname files with all agents>

if [ $# -lt 2 ]; then
    echo "usage: ./set_ambari_server_network.sh <Weave internal IP> <Weave DNS IP> <Mask>"
    echo "example: ./set_ambari_server_network.sh 192.168.10.10 192.168.10.11 16"
    exit 1
fi

Weave_internal_IP=$1
Weave_DNS_IP=$2
mask=$3

# install weave
chmod 755 ../Linux/CentOS7/weave_install.sh
../Linux/CentOS7/weave_install.sh

# install docker
chmod 755 ../Linux/CentOS7/docker_install.sh
../Linux/CentOS7/docker_install.sh

# reset weave
weave reset

# launch weave
weave launch

# expose IP
weave expose "${Weave_internal_IP}/${mask}"

# launch Weave DNS
weave launch-dns "${Weave_DNS_IP}/${mask}"

# edit /etc/resolv.conf file

