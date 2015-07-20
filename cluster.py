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
import time
from config import Config
from docker import Docker
from vm import VM
import os
from log import Log

class Cluster:
    """
    The Cluster instance holds a list of VMs, and has the methods to request cluster, generate information and run all Ambari-agent
    """
    def __init__(self):
        self.cluster_name = ""
        self.VMs_num = 0
        self.VM_list = []

    def load_cluster_info(self, filename):
        """
        read cluster info from a file
        :param filename: name of the cluster infomation file
        :return: None
        """
        with open(filename) as file:
            self.cluster_name = file.next().split()[1]
            self.VMs_num = int(file.next().split()[1])
            for VM_index in range(0, self.VMs_num):
                IP = file.next().split()[1]
                domain_name = file.next().split()[1]
                Weave_DNS_IP = file.next().split()[1]
                vm = VM(IP, domain_name, Weave_DNS_IP)
                docker_num = int(file.next().split()[1])
                for Docker_index in range(0, docker_num):
                    line = file.next()
                    IP = line.split()[0].split("/")[0]
                    mask = line.split()[0].split("/")[1]
                    Weave_domain_name = line.split()[1]
                    docker = Docker(IP, mask,  Weave_domain_name)
                    vm.add_docker(docker)
                self.VM_list.append(vm)

    def __extract_VM_IP__(self, GCE_info_file_name):
        """
        exatract IP address of VMs from the output file of GCE
        :param GCE_info_file_name: output file of "GCE info" command
        :return: the IP address List
        """
        with open(GCE_info_file_name) as f:
            lines = f.readlines()

        ip_list = []
        for line in lines:
            tokens = line.split()
            ip_list.append(tokens[1])
        return ip_list[1:]

    def __extract_VM_FQDN_IP__(self, GCE_info_file_name):
        """
        exatract domain name and IP address of VMs from the output file of GCE
        :param GCE_info_file_name: output file of "GCE info" command
        :return: A list of tuple, each tuple has domain name and IP of a VM
        """
        with open(GCE_info_file_name) as f:
            lines = f.readlines()

        VM_list = []
        for line in lines:
            tokens = line.split()
            FQDN_IP = (tokens[0], tokens[1])
            VM_list.append(FQDN_IP)
        return VM_list[1:]

    def request_GCE_cluster(self, vms_num, docker_num, cluster_name):
        """
        request a new cluster from GCE
        :param vms_num: the number of GCE VM
        :param docker_num: the number of Docker containers inside each VM
        :param cluster_name: the name of the cluster
        :return: None
        """

        # request cluster
        gce_key = Config.ATTRIBUTES["GCE_controller_key_file"]
        gce_login = "{0}@{1}".format(Config.ATTRIBUTES["GCE_controller_user"], Config.ATTRIBUTES["GCE_controller_IP"])
        gce_up_cmd = "gce up {0} {1} {2} {3}".format(cluster_name, vms_num, Config.ATTRIBUTES["GCE_VM_type"], Config.ATTRIBUTES["GCE_VM_OS"])

        if "GCE_extra_disk" in Config.ATTRIBUTES:
            gce_up_cmd = "{0} {1}".format(gce_up_cmd, Config.ATTRIBUTES["GCE_extra_disk"])

        subprocess.call(["ssh", "-o", "StrictHostKeyChecking=no", "-i", gce_key, gce_login, gce_up_cmd])

        Log.write("cluster launched, wait for cluster info ... ...")

        for retry in range(3):
            time.sleep(10)

            # request cluster info
            with open(Config.ATTRIBUTES["GCE_info_output"], "w") as gce_info_output_file:
                gce_info_cmd = "gce info {0}".format(cluster_name)
                subprocess.call(["ssh", "-o", "StrictHostKeyChecking=no", "-i", gce_key, gce_login, gce_info_cmd], \
                                stdout=gce_info_output_file)

            VM_list = self.__extract_VM_FQDN_IP__(Config.ATTRIBUTES["GCE_info_output"])

            if len(VM_list) == vms_num:
                Log.write("Get info for all ", str(len(VM_list)), " VMs successfully")
                break
            Log.write("Only get info for ", str(len(VM_list)), " VMs, retry ... ...")
        Log.write("cluster info is saved to file ", Config.ATTRIBUTES["GCE_info_output"])

        # prepare all attributes of the cluster, write to a file
        self.generate_cluster_info(VM_list, cluster_name, docker_num)
        self.overwrite_to_file(Config.ATTRIBUTES["cluster_info_file"])

    def overwrite_to_file(self, filename):
        """
        save the information of the cluster to file
        :param filename: the name of the file to save the cluter information
        :return: None
        """
        with open(filename, "w") as file:
            file.write("cluster_name: {0}\n".format(self.cluster_name))
            file.write("VMs_num: {0}\n".format(self.VMs_num))

            for vm in self.VM_list:
                file.write("\t\tVM_IP: {0}\n".format(vm.external_ip))
                file.write("\t\tVM_domain_name: {0}\n".format(vm.domain_name ))
                file.write("\t\tWeave_DNS_IP: {0}\n".format(vm.Weave_DNS_IP))
                file.write("\t\tDocker_num: {0}\n".format(len(vm.docker_list)))
                for docker in vm.docker_list:
                    file.write("\t\t\t\t{0}/{1} {2}\n".format(docker.IP, docker.mask, docker.Weave_domain_name))

    def __increase_IP__(self, base_IP, increase):
        """
        increase the IP address.
        example: 192.168.1.1, increased by 1: 192.168.1.2
        example: 192.168.1.254, increased by 2: 192.168.2.1
        :param base_IP: the IP to be increased
        :param increase: the amount of increase
        :return: the new IP address, in a integer List
        """
        IP = [int(base_IP[0]), int(base_IP[1]), int(base_IP[2]), int(base_IP[3])]
        IP[3] = IP[3] + increase
        for index in reversed(range(0, 4)):
            if IP[index] > 255:
                IP[index - 1] = IP[index - 1] + IP[index] / 256
                IP[index] = IP[index] % 256
        return IP

    def generate_cluster_info(self, VM_list, cluster_name, docker_num):
        """
        generate VM and docker info for this cluster
        set up parameter of the class instance as this info
        :param VM_list: the domain name and IP address pairs List of all VMs
        :param cluster_name: the name of the cluster
        :param docker_num: the number of Docker containers inside each VM
        :return: None
        """
        Docker_IP_base = Config.ATTRIBUTES["Docker_IP_base"].split(".")
        Docker_IP_mask = Config.ATTRIBUTES["Docker_IP_mask"]

        current_IP = Docker_IP_base
        VM_index = 0
        for VM_domain_name, VM_IP in VM_list:
            current_IP = self.__increase_IP__(current_IP, 1)
            Weave_DNS_IP = "{0}.{1}.{2}.{3}".format(current_IP[0], current_IP[1], current_IP[2], current_IP[3])
            vm = VM(VM_IP, VM_domain_name, Weave_DNS_IP)

            for Docker_index in range(0, docker_num):
                current_IP = self.__increase_IP__(current_IP, 1)
                docker_IP_str = "{0}.{1}.{2}.{3}".format(current_IP[0], current_IP[1], current_IP[2], current_IP[3])

                total_Docker_index = VM_index * docker_num + Docker_index
                docker_hostname = Docker.get_Weave_domain_name(cluster_name, total_Docker_index)

                docker = Docker(docker_IP_str, str(Docker_IP_mask), docker_hostname)
                # print docker
                vm.add_docker(docker)

            VM_index = VM_index + 1
            self.VM_list.append(vm)

        self.VMs_num = len(VM_list)
        self.cluster_name = cluster_name

    def run_docker_on_cluster(self, server_external_IP, server_Weave_IP):
        """
        run all dockers for all the VMs in the cluster
        upload necessary file to each machine in cluster, run launcher_docker.py in each machine with parameter
        :param server_external_IP: the external IP address of ambari-server
        :param server_Weave_IP: the Weave internal IP address of ambari-server
        :return: None
        """
        VM_output_file_list = []
        process_list = []
        terminate_state_list = []

        for vm in self.VM_list:
            # open file for the output
            VM_output_file_path = vm.__get_SSH_output_file_path__()
            VM_output_file = open(VM_output_file_path, "w")
            VM_output_file_list.append(VM_output_file)

            # upload necessary file to each machine in cluster
            VM_external_IP = vm.external_ip
            VM_directory = "{0}@{1}:{2}".format(Config.ATTRIBUTES["VM_user"], VM_external_IP, Config.ATTRIBUTES["VM_code_directory"])
            VM_key = Config.ATTRIBUTES["VM_key_file"]

            upload_return_code = 0
            with open(os.devnull, 'w') as shutup:
                upload_return_code = subprocess.call(["scp", "-o", "StrictHostKeyChecking=no", "-i", VM_key, "-r", ".", VM_directory], \
                            stdout=shutup, stderr=shutup)
            if upload_return_code == 0:
                Log.write("VM ", VM_external_IP, " file upload succeed")
            else:
                Log.write("VM ", VM_external_IP, " file upload fail")

            VM_ssh_login = "{0}@{1}".format(Config.ATTRIBUTES["VM_user"], VM_external_IP)

            VM_ssh_cd_cmd = "cd {0}".format(Config.ATTRIBUTES["VM_code_directory"])
            VM_ssh_python_cmd = "python launcher_docker.py {0} {1} {2}".format(VM_external_IP, server_Weave_IP, server_external_IP)
            VM_ssh_cmd = "{0};{1}".format(VM_ssh_cd_cmd, VM_ssh_python_cmd)

            process = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no", "-t", "-i", VM_key, \
                                        VM_ssh_login, VM_ssh_cmd], \
                                       stdout=VM_output_file, stderr=VM_output_file)

            process_list.append(process)

            terminate_state_list.append(False)
            Log.write("Configuring VM ", vm.external_ip, " ... ...")

        Log.write("Wait for all VMs to finish configuration ... ...")

        while True:
            all_finished = True
            for index in range(len(self.VM_list)):
                if terminate_state_list[index] == False:
                    all_finished = False
                    returncode = process_list[index].poll()
                    if returncode is None:
                        continue
                    else:
                        VM_output_file_path =  self.VM_list[index].__get_SSH_output_file_path__()
                        Log.write("VM ", self.VM_list[index].external_ip, " configuration completed, return code: ", str(returncode) \
                            , ", output file path: ", VM_output_file_path)
                        terminate_state_list[index] = True
                        VM_output_file_list[index].close()
                else:
                    pass
            if all_finished:
                break
            time.sleep(5)

        Log.write("All VM configuration completed.")
