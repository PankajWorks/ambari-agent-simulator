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

from config import Config

class Docker:
    """
    Docker represents a Docker container, each with its IP and hostname
    """
    def __init__(self, IP, mask, hostname):
        self.IP = IP
        self.mask = mask
        self.hostname = hostname

    def __str__(self):
        return str(self.IP) + "/" + str(self.mask) + " " + self.hostname

    @staticmethod
    def get_hostname(cluster_name, index):
        """
        given the index and the name of cluster, generate the hostname for the docker
        :param cluster_name:
        :param index:
        :return: hostname of the docker
        """
        return Config.ATTRIBUTES["Container_hostname_fix"] + "-" + str(index) + "-" + cluster_name

    @staticmethod
    def get_index(hostname):
        """
        given the hostname of docker, extract the index of the docker within the cluster
        :param hostname:
        :return: the index
        """
        return hostname.split("-")[1]

    @staticmethod
    def get_container_name(hostname):
        """
        give the hostname of docker, get the name of the container
        :param hostname:
        :return: the name of the container
        """
        return hostname