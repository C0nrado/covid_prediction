# This module implements a class for managing http api's based on custom YAML config files.

import requests
import hashlib
import yaml
import re
import os
import os.path as path
from collections import defaultdict

def rename_keys(kval_pair, key='name'):
    old_key, contents = kval_pair 
    if key in contents.keys():
        new_key = contents[key]
        contents.pop(key)
    else:
        new_key = old_key

    return new_key, contents

class apiManager():
    def __init__(self, path, base_dir, monitor_api=False):
        if os.path.isdir(base_dir):
            self.base_directory = os.path.abspath(base_dir)
        self._monitor_api = monitor_api
        self._parse_config_file(path)

    def fetch(self):
        self._make_dirs()
        for endpoint_name in self.endpoints:
            endpoint_api_string = self._get_api_string(endpoint_name)
            url = self.api + endpoint_api_string
            filename = self._get_filename(endpoint_name)
            file_out = os.path.join(self.base_directory, endpoint_name, filename)
            response = requests.get(url)

            with open(file_out, 'wb') as out:
                out.write(response.content)

    def _parse_config_file(self, path):
        with open(path) as file:
            api_config = yaml.load(file, Loader=yaml.FullLoader)
            
            # renaming main api entries
            api_config = dict(map(rename_keys, api_config.items()))
            self.name, contents = api_config.popitem()

            # renaming possible endpoints
            print(contents.keys())
            if 'endpoints' in contents.keys():
                renamed_endpoints = dict(
                        map(lambda pair: rename_keys(pair), enumerate(contents['endpoints']))
                    )
                contents['endpoints'] = renamed_endpoints
            
            self.api = contents['api']
            self.endpoints = contents['endpoints']

            if self._monitor_api:
                self.status = contents['status']
    
    def _make_dirs(self):

        for endpoint_name in self.endpoints:
            dir_path = os.path.join(self.base_directory, endpoint_name)
            os.makedirs(dir_path, exist_ok=True)
   
    def _get_api_string(self, endpoint_name):
        return self.endpoints[endpoint_name]['api']

    def _get_filename(self, endpoint_name):
        api_string = self._get_api_string(endpoint_name)
        return re.match(r".*/(.*)$", api_string).group(1)
 

# code for testing purposes
if __name__ == '__main__':
    path = './.config/covid_api.yml'
    covid_api = apiManager(path=path, base_dir='./.cache', monitor_api=True)
    print(covid_api.name)
    print(covid_api.api)
    print(covid_api.status['keys'])
    print(len(covid_api.endpoints))
    print(covid_api.base_directory)

    covid_api.fetch()