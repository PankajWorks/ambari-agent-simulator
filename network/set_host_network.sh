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

# This script is used to add a Host/VM to the Docker network
# for example, an Ambari-agent withn a VM (not in a Docker container)

if [ $# -lt 3 ]; then
    echo "usage: ./set_ambari_server_network.sh <Weave internal IP> <Weave DNS IP> <Mask> <Ambari server IP>"
    echo "example: ./set_ambari_server_network.sh 192.168.254.1 192.168.254.2 16 104.196.91.170"
    exit 1
fi

Weave_internal_IP=$1
Weave_DNS_IP=$2
mask=$3
Ambari_server_IP=$4

# install weave
chmod 755 ../Linux/CentOS7/weave_install.sh
../Linux/CentOS7/weave_install.sh

# install docker
chmod 755 ../Linux/CentOS7/docker_install.sh
../Linux/CentOS7/docker_install.sh

# reset weave
weave reset

# launch weave
weave launch ${Ambari_server_IP}/${mask}

# expose IP
weave expose ${Weave_internal_IP}/${mask}

# launch Weave DNS
weave launch-dns ${Weave_DNS_IP}/${mask}

# edit /etc/resolv.conf file
python DNS_editor.py $Weave_DNS_IP