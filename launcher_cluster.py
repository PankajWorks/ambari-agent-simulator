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


import time
import sys
from cluster import Cluster
from config import Config
from data import Data

def request_cluster(argv):
    """
    only request cluster on GCE, and output all configuration information
    :param argv: sys.argv
    :return: None
    """
    if len(argv) < 7:
        print_help()
        exit(1)

    cluster_name = argv[2]
    ambari_agent_vm_num = int(argv[3])
    docker_num = int(argv[4])
    service_server_num = int(argv[5])
    with_ambari_server = False
    ambari_server_num = int(argv[6])
    if ambari_server_num > 0:
        with_ambari_server = True

    cluster = Cluster()
    cluster.request_gce_cluster(ambari_agent_vm_num, docker_num, service_server_num, with_ambari_server, cluster_name)

    data = Data()
    data.set_cluster_state(cluster.cluster_name, Cluster.STATE_FREE)

    time_to_wait = Config.ATTRIBUTES["GCE_boot_time"]
    print "wait ", str(time_to_wait), " seconds for the cluster to boot ... ..."
    time.sleep(int(time_to_wait))
    print "complete"

def _confirm_free_state(cluster_name):
    data = Data()
    state_name = data.get_cluster_state(cluster_name)
    if state_name is None:
        print cluster_name, " cluster not found"
        exit(1)
    elif state_name != Cluster.STATE_FREE:
        print cluster_name, " cluster is already running"
        exit(1)

def _confirm_run_state(cluster_name):
    data = Data()
    state_name = data.get_cluster_state(cluster_name)
    if state_name is None:
        print cluster_name, " cluster not found"
        exit(1)
    elif state_name != Cluster.STATE_RUNNING:
        print cluster_name, " cluster is not running or has no Ambari-server, can't be extended"
        exit(1)

def up_cluster(argv):
    """
    run all Docker containers in the cluster according to the configuration file
    :param argv: sys.argv
    :return: None
    """
    if len(argv) < 3:
        print_help()
        exit(1)

    cluster_name = argv[2]
    _confirm_free_state(cluster_name)

    print "Configuring cluster"
    print "Check output folder: ", Config.ATTRIBUTES["Output_folder"]
    cluster = Cluster.load_from_json(cluster_name)
    ambari_server = cluster.get_ambari_server_vm()

    if ambari_server is None:
        print "Unable to run cluster", cluster_name ," no Ambari-server."

    cluster.run_cluster(ambari_server.weave_internal_ip, ambari_server.external_ip)
    data = Data()
    data.set_cluster_state(cluster_name, Cluster.STATE_RUNNING)
    print "Complete"

def merge_cluster(argv):
    if len(argv) < 4:
        print_help()
        exit(1)

    merged_cluster_name = argv[2]
    _confirm_free_state(merged_cluster_name)

    weave_ip = ""
    external_ip = ""
    if len(argv) == 4:
        extended_cluster_name = argv[3]
        _confirm_run_state(extended_cluster_name)
        extended_cluster = Cluster.load_from_json(extended_cluster_name)
        ambari_server = extended_cluster.get_ambari_server_vm()
        weave_ip = ambari_server.weave_internal_ip
        external_ip = ambari_server.external_ip

    elif len(argv) == 5:
        weave_ip = argv[3]
        external_ip = argv[4]

    else:
        print_help()
        exit(1)

    print "Configuring cluster"
    print "Check output folder: ", Config.ATTRIBUTES["Output_folder"]
    merged_cluster = Cluster.load_from_json(merged_cluster_name)
    merged_cluster.run_cluster(weave_ip, external_ip)

    data = Data()
    data.set_cluster_state(merged_cluster_name, Cluster.STATE_MERGE)
    print "Complete"


def print_help():
    """
    print help information
    example python launcher_cluster.py all test-cluster 2 3 192.168.255.1 104.196.84.248
    :return: None
    """
    print "usage:"
    print

    print "request", "  ", "--request a cluster from GCE, generate the configuration for the cluster"
    print "\t\t", "<the name of the cluster>"
    print "\t\t", "<number of VMs>"
    print "\t\t", "<number of dockers each VM>"
    print "\t\t", "<number of service servers inside VM>"
    print "\t\t", "<number of ambari-server>, either 0 or 1"
    print

    print "up", "  ", "--run all Ambari-agents and Ambari-server of the cluster"
    print "\t\t", "<the name of the cluster>"
    print

    print "merge", "  ", "--run one cluster, and add to another cluster"
    print "\t\t", "<the name of the cluster to be merged>"
    print "\t\t", "<the name of the cluster to be extended>"
    print

    print "merge", "  ", "--run one cluster, and add to another cluster"
    print "\t\t", "<the name of the cluster to be merged>"
    print "\t\t", "<Weave IP of the Ambari-server>"
    print "\t\t", "<External IP of the Ambari-server>"
    print

    print "help", "  ", "help info"
    print

def main(argv):
    # the first argument is the python file name
    if len(argv) < 2:
        print_help()
        exit(1)

    command = argv[1]

    if command == "request":
        request_cluster(argv)

    elif command == "up":
        up_cluster(argv)

    elif command == "merge":
        merge_cluster(argv)

    elif command == "help":
        print_help()

    else:
        print_help()

if __name__ == "__main__":
    Config.load()
    main(sys.argv)



