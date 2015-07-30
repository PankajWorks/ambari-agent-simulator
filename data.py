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

import os.path
import json
from config import Config

class Data:
    def __init__(self):
        self.data_filename = Config.ATTRIBUTES["cluster_info_file"]

    def _load_data(self):
        json_data = {"clusters":[]}
        if os.path.isfile(self.data_filename):
            with open(self.data_filename) as file:
                json_data = json.load(file)
        return json_data

    def _save_data(self, json_data):
        with open(self.data_filename, "w") as file:
            json.dump(json_data, file, indent=4, separators=(',', ': '))

    def add_new_cluster(self, cluster):
        """
        save the information of the cluster to file
        :param filename: the name of the file to save the cluter information
        :return: None
        """
        json_data = self._load_data()
        new_cluster_json = cluster.to_json()
        json_data["clusters"].insert(0, new_cluster_json)
        self._save_data(json_data)

    def set_cluster_state(self, cluster_name, state_name):
        json_data = self._load_data()
        for cluster in json_data["clusters"]:
            if cluster["cluster_name"] == cluster_name:
                state = {"state_name": state_name}
                cluster["state"] = state
                break
        self._save_data(json_data)

    def get_cluster_state(self, cluster_name):
        json_data = self._load_data()
        for cluster in json_data["clusters"]:
            if cluster["cluster_name"] == cluster_name:
                return cluster["state"]["state_name"]
        return None

    def read_cluster_json(self, cluster_name):
        json_data = self._load_data()
        for cluster_json in json_data["clusters"]:
            if cluster_json["cluster_name"] == cluster_name:
                return cluster_json
