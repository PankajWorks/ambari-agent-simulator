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
from cluster import Cluster
import sys

if __name__ == "__main__":
    Config.load()

    my_external_ip = sys.argv[1]
    server_weave_ip = sys.argv[2]
    server_external_ip = sys.argv[3]
    cluster_name = sys.argv[4]

    cluster = Cluster.load_from_json(cluster_name)

    vm = cluster.get_service_server_vm(my_external_ip)
    vm.run_service_server(server_weave_ip, server_external_ip)