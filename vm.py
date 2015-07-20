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
import shutil
from config import Config
import os

class VM:
    """
    This class represents VM, each VM instance has multiple Docker inside
    """
    def __init__(self, external_ip, domain_name, Weave_DNS_IP):
        self.external_ip = external_ip
        self.domain_name = domain_name
        self.hostname = self.__GCE_get_hostname__(domain_name)
        self.Weave_DNS_IP = Weave_DNS_IP
        self.docker_list = []

    def __GCE_get_hostname__(self, domain_name):
        """
        The hostname of GCE VM is the first part of the internal domain name
        :param domain_name: the internal domain name of GCE VM
        :return: the hostname of GCE VM
        """
        return domain_name.split(".")[0]

    def __get_SSH_output_file_path__(self):
        VM_output_file_path = "{0}/VM-{1}-{2}".format(Config.ATTRIBUTES["Output_folder"], self.hostname, self.external_ip)
        return VM_output_file_path


    def add_docker(self, docker):
        self.docker_list.append(docker)

    def __centos7_weave_install__(self):
        """
        install Weave on this VM
        :return: None
        """
        subprocess.call(["sudo", "chmod", "755", "Linux/CentOS7/weave_install.sh"])
        subprocess.call("./Linux/CentOS7/weave_install.sh")

    def __set_weave_network__(self, VMs_external_IP_list, server_external_ip, Weave_DNS_IP):
        """
        launch Weave, make this VM connect with other VM
        :param VMs_external_IP_list: external IP List of all VMs
        :param server_external_ip: the external IP of the Ambari-server
        :return: None
        """
        # add other VMs and the ambari-server to set up connections
        weave_launch_command = ["sudo", "weave", "launch"]
        weave_launch_command.extend(VMs_external_IP_list)
        weave_launch_command.append(server_external_ip)
        with open(os.devnull, 'w') as shutup:
            subprocess.call(weave_launch_command, stdout=shutup)

        # establish DNS server
        Weave_DNS_IP_with_mask = "{0}/{1}".format(Weave_DNS_IP, Config.ATTRIBUTES["Docker_IP_mask"])
        weave_launch_DNS_command = ["sudo", "weave", "launch-dns", Weave_DNS_IP_with_mask]
        subprocess.call(weave_launch_DNS_command)

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
        # choose the right Dockerfile
        target_Dockerfile_name = "Docker/{0}".format(Config.ATTRIBUTES["Dockerfile_name"])
        standard_Dockerfile_name = "Docker/Dockerfile"
        shutil.copyfile(target_Dockerfile_name, standard_Dockerfile_name)
        with open(os.devnull, 'w') as shutup:
            subprocess.call(["sudo", "docker", "build", "-q", "-t", image_name, "Docker/"], stdout=shutup)
        os.remove(standard_Dockerfile_name)

    def __pull_docker_image__(self, image_name):
        with open(os.devnull, 'w') as shutup:
            subprocess.call(["sudo", "docker", "pull", image_name], stdout=shutup)

    def __launch_containers__(self, docker_image, server_weave_ip):
        """
        launch Docker containers, issue the script to install, configure and launch Agent inside Docker.
        :param docker_image: the name of the Docker image
        :param server_weave_ip: Weave internal IP of Ambari-server
        :return: None
        """
        # print docker_ip_list
        for docker in self.docker_list:
            docker_IP_with_mask = "{0}/{1}".format(docker.IP, docker.mask)
            cmd = "python /launcher_agent.py {0} {1}; /bin/bash".format(server_weave_ip, docker.IP)

            command = ["sudo", "weave", "run", docker_IP_with_mask, "-d", "-it", \
                       "-h", docker.Weave_domain_name, \
                       "--name", docker.get_container_name(), \
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

        self.__centos7_docker_install__()

        if "Use_partition" in Config.ATTRIBUTES:
            self.__set_docker_partition__(Config.ATTRIBUTES["Use_partition"])

        self.__centos7_weave_install__()

        image_name = Config.ATTRIBUTES["Docker_image_name"]
        if "Pull_Docker_Hub" in Config.ATTRIBUTES and Config.ATTRIBUTES["Pull_Docker_Hub"] == "yes":
            self.__pull_docker_image__(image_name)
        else:
            self.__build_docker_image__(image_name)

        self.__set_weave_network__(VMs_IP_list, server_external_IP, self.Weave_DNS_IP)
        self.__launch_containers__(Config.ATTRIBUTES["Docker_image_name"], server_weave_IP)