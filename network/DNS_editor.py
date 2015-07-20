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

local_nameserver_IP = sys.argv[1]

nameserver_file_name = "/etc/resolv.conf"
with open(nameserver_file_name) as f:
    lines = f.readlines()

add_nameserver = False
with open(nameserver_file_name, "w+") as f:
    for line in lines:
        if "search" in line:
            tokens = line.split()
            f.write("search weave.local ")
            for token in tokens[2:]:
                f.write(token)
            f.write("\n")
        if "nameserver" in line:

            f.write("nameserver ")
        else:
            f.write(line)