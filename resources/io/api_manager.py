# This module implements a class for managing http api's based on custom YAML config files.

import requests
import hashlib
import yaml
import os
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
        self.apis = self._parse_config_file(path)

    def _parse_config_file(self, path):
        with open(path) as file:
            api_config = yaml.load(file, Loader=yaml.FullLoader)
            
            # renaming main api entries
            api_config = dict(map(rename_keys, api_config.items()))

            # renaming possible endpoints
            for main_entry in api_config:
                entry = api_config[main_entry]
                if 'endpoints' in entry.keys():
                    renamed_endpoints = dict(
                            map(lambda pair: rename_keys(pair), enumerate(entry['endpoints']))
                    )
                    entry['endpoints'] = renamed_endpoints

        return api_config

# code for testing purposes
if __name__ == '__main__':
    path = './.config/covid_api.yml'
    covid_api = apiManager(path=path, base_dir=False)
    print(covid_api.apis)
    print(type(covid_api.apis))