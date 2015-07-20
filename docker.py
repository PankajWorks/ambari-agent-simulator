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
    def __init__(self, IP, mask, Weave_domain_name):
        self.IP = IP
        self.mask = mask
        self.Weave_domain_name = Weave_domain_name

    def __str__(self):
        return str(self.IP) + "/" + str(self.mask) + " " + self.Weave_domain_name

    @staticmethod
    def get_Weave_domain_name(cluster_name, index):
        """
        given the index and the name of cluster, generate the  Weave domain name for the docker
        :param cluster_name:
        :param index:
        :return: Weave domain name of the docker container
        """
        return "{0}-{1}-{2}.{3}".format(Config.ATTRIBUTES["Container_hostname_fix"], index, cluster_name, "weave.local")

    def get_index(self):
        """
        extract the index of the docker within the cluster
        :return: the index
        """
        return self.Weave_domain_name.split("-")[1]

    def get_container_name(self):
        """
        :return: the name of the container
        """
        return self.get_hostname()

    def get_hostname(self):
        return self.Weave_domain_name.split(".")[0]