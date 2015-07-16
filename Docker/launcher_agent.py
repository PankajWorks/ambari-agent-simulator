'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import sys
import subprocess
import time

def replace_conf(server_ip):
    """
    replace the server host IP in the Ambari-agent configuration file
    :param server_ip: internal Weave IP address of Ambari-server
    :return: None
    """
    with open("/etc/ambari-agent/conf/ambari-agent.ini") as f:
        lines = f.readlines()

    with open("/etc/ambari-agent/conf/ambari-agent.ini", "w+") as f:
        for line in lines:
            line = line.replace("hostname=localhost", "hostname=" + server_ip)
            f.write(line)

def run_ambari_agent():
    """
    command line to run Ambari-agent
    :return: None
    """
    # command = ["sudo", "ambari-agent", "start"]
    # subprocess.call(command)
    subprocess.call("./ambari_agent_start.sh")

def add_hostnames(agent_hosts_file, hostname):
    """
    add all the hostnames of other containers to /etc/hosts
    :param agent_hosts_file: the file with all hostname IP mapping of agents
    :return: None
    """
    with open("/etc/hosts", "a") as etc_hosts:
        etc_hosts.write("\n")
        with open(agent_hosts_file) as docker_hosts:
            for line in docker_hosts.readlines():
                if hostname in line:
                    etc_hosts.write(line)

def remove_default_hostname(hostname):
    """
    remove the default hostname IP mapping which is added by Docker
    :param hostname: the hostname of the Docker
    :return: None
    """
    with open("/etc/hosts") as etc_hosts:
        all_resolution = etc_hosts.readlines()

    with open("/etc/hosts", "w") as etc_hosts:
        for line in all_resolution:
            if hostname not in line:
                etc_hosts.write(line)
            else:
                etc_hosts.write("#")
                etc_hosts.write(line)

def main():
    ambari_server_ip = sys.argv[1]
    my_hostname = sys.argv[2]
    replace_conf(ambari_server_ip)
    remove_default_hostname(my_hostname)
    add_hostnames("/hosts", my_hostname)
    run_ambari_agent()

if __name__ == "__main__":
    main()