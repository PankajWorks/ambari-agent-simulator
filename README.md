<!---
Licensed to the Apache Software Foundation (ASF) under one or more
contributor license agreements.  See the NOTICE file distributed with
this work for additional information regarding copyright ownership.
The ASF licenses this file to You under the Apache License, Version 2.0
(the "License"); you may not use this file except in compliance with
the License.  You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

Ambari-agent Simulator
============
This project provides a tool to create a large Ambari-agent cluster in a convenient way.

## Usage:
Run python launcher_cluster.py to see usage

python launcher_cluster.py all    

    request a GCE cluster and run Docker containers with Ambari-agent in all VMs. Parameters:
	<the name of the cluster>
	<number of VMs>
	<number of dockers each VMs>
	<Weave IP of Ambari-server>
	<IP of Ambari-server>
		
python launcher_cluster.py request
        
    request a cluster from GCE, generate the configuration for the cluster. Parameters:
	<the name of the cluster>
	<number of VMs>
	<number of dockers each VMs>
		
python launcher_cluster.py run    

    run Docker containers with Ambari-agent in all VMs of the cluster. Parameters:
	<Weave IP of Ambari-server>
	<IP of Ambari-server>

python launcher_cluster.py help    
        
    show help info

## Work Flow:
* Step 1: Install Ambari-server


    Use existing Ambari-server, or, install and launch a new one
    
* Step 2: Decide IP in your mind


    Mark down the IP of the Ambari-server, say 104.196.81.81
    Come up a subnet say 192.168.#.#/16
    Pick one address closer to the END of the subnet as the Weave INTERNAL IP of Ambari-server, say 192.168.100.100
    Pick one address closer to the START of the subnet as the Weave INTERNAL IP of the FIRST Ambari-agent, say 192.168.2.2
    Other Weave INTERNAL IP of Amari-agent will be automatically assigned based on the FIRST one (increasingly).
    
* Step 3: Modify config.ini


    Modify attributes: Output_folder, GCE_controller_key_file, GCE_VM_key_file
    Change Docker_IP_base and Docker_IP_mask according to Step 2: 192.168.2.2 and 16
    
* Step 4: Request Ambari-agent cluster


    Run python launcher_cluster.py request
    cluster.txt file will appear under directory ./config within 1 minutes
    
* Step 5: Run Ambari-agent Cluster


    Modify cluster.txt file to configure the cluster
    Run python launcher_cluster.py run
    

* Step 6: First time set up Ambari-server


    Copy all the agent-simulator code base to Ambari-server
    Run server_setup.sh with the Weave INTERNAL IP of Ambari-server decided in Step 2, 192.168.100.100, and the hosts.txt file as parameters
    
* Extra: Add more Ambari-agents to Ambari-server (already set up)


    Do Step 4 and 5 again
    
## Expand Cluster With This Script 
Be careful if you wanna use this script to add more Ambari-agents AGAIN to your Ambari-server

* Use different Cluster Name when providing parameters to launcher_cluster.py
* In config.ini, use the same Docker_IP_mask, make sure the same subnet
* Change config.ini to use different Docker_IP_base, make sure that all new IPs never overlap with the existing IPs
* Change config.ini to use different Container_hostname_fix, make sure that all Docker containers have different names and host names
* Change config.ini to use different cluster_info_file, make sure the existing cluster information is not overwritten
   
## Expand Cluster By Adding other Hosts/VMs
   
## Naming Convention
Cluster Name, VM Name, Docker Name

## Configure and Inspect the Cluster

## Use Image for Docker Container

## Use Different Partition for Docker Container

## Suggestions:
* Use CTRL + P, then CTRL + Q to exit Docker container
    Use "exit" will terminate the container.
    How to bring it back, if you terminated one Docker?
* Remove ~/.ssh/know_hosts files, especially if you run a large cluster
    You might get a warning from SSH, because the new GCE VM assigned to you might have the same IP with the VMs you saved in know_hosts file. Remove .ssh/know_hosts before run this script.
* Ambari-agent and Ambari-server have to be the same version to successfully register. 
    The command used to install Ambari-agent is in the Dockerfile