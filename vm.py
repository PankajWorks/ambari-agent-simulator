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


import subprocess
from config import Config
from docker import Docker

class VM:
    """
    This class represents VM, each VM instance has multiple Docker inside
    """
    def __init__(self, external_ip, DNS):
        self.external_ip = external_ip
        self.DNS = DNS
        self.hostname = self.__GCE_get_hostname__(DNS)
        self.docker_list = []

    def __GCE_get_hostname__(self, DNS):
        """
        The hostname of GCE VM is the first part of the internal DNS
        :param DNS: the internal DNS of GCE VM
        :return: the hostname of GCE VM
        """
        return DNS.split(".")[0]

    def add_docker(self, docker):
        self.docker_list.append(docker)

    def __centos7_weave_install__(self):
        """
        install Weave on this VM
        :return: None
        """
        subprocess.call(["sudo", "chmod", "755", "Linux/CentOS7/weave_install.sh"])
        subprocess.call("./Linux/CentOS7/weave_install.sh")

    def __set_weave_network__(self, VMs_external_IP_list, server_external_ip):
        """
        launch Weave, make this VM connect with other VM
        :param VMs_external_IP_list: external IP List of all VMs
        :param server_external_ip: the external IP of the Ambari-server
        :return: None
        """
        # add other VMs and the ambari-server to set up connections
        command = ["sudo", "weave", "launch"]
        command.extend(VMs_external_IP_list)
        command.append(server_external_ip)
        subprocess.call(command)

    def __centos7_docker_install__(self):
        """
        install Docker on this VM
        :return: None
        """
        subprocess.call(["sudo", "chmod", "755", "Linux/CentOS7/docker_install.sh"])
        subprocess.call("./Linux/CentOS7/docker_install.sh")

    def __build_docker_image__(self, image_name):
        """
        build docker image
        :param image_name: the name of the Docker image
        :return: None
        """
        subprocess.call(["sudo", "docker", "build", "-t", image_name, "Docker/"])

    def __launch_containers__(self, docker_image, server_weave_ip):
        """
        launch Docker containers, issue the script to install, configure and launch Agent inside Docker.
        :param docker_image: the name of the Docker image
        :param server_weave_ip: Weave internal IP of Ambari-server
        :return: None
        """
        # print docker_ip_list
        for docker in self.docker_list:
            docker_IP = docker.IP
            docker_mask = docker.mask
            docker_hostname = docker.hostname

            cmd = "python /launcher_agent.py " + server_weave_ip + " " + docker_hostname + "; /bin/bash"
            command = ["sudo", "weave", "run", docker_IP + "/" + docker_mask, "-d", "-it", \
                       "-h", docker_hostname, \
                       "--name", Docker.get_container_name(docker_hostname), \
                       docker_image, "bash", "-c", cmd]
            print command
            subprocess.call(command)

    def __set_docker_partition__(self, mount_point):
        """
        set docker container use the disk storage of other partitions.
        :param mount_point: the mount point of the partion to be used
        :return: None
        """
        subprocess.call(["sudo", "chmod", "755", "./Linux/CentOS7/set_docker_partition.sh"])
        subprocess.call(["./Linux/CentOS7/set_docker_partition.sh", mount_point])

    def run_docker(self, server_weave_IP, server_external_IP, cluster):
        """
        run all Docker containers with Ambari-agent inside
        :param server_weave_IP: Weave internal IP of Ambari-server
        :param server_external_IP: external IP of Ambari-server
        :param cluster: the cluster instance
        :return: None
        """
        VMs_IP_list = []
        for vm in cluster.VM_list:
            VMs_IP_list.append(vm.external_ip)

        cluster.export_hostnames("./Docker/hosts")

        self.__centos7_docker_install__()

        if "Use_partition" in Config.ATTRIBUTES:
            self.__set_docker_partition__(Config.ATTRIBUTES["Use_partition"])

        self.__centos7_weave_install__()
        self.__build_docker_image__(Config.ATTRIBUTES["Docker_image_name"])
        self.__set_weave_network__(VMs_IP_list, server_external_IP)
        self.__launch_containers__(Config.ATTRIBUTES["Docker_image_name"], server_weave_IP)