# This module implements a class for managing http api's based on custom YAML config files.

import requests
import hashlib
import yaml
import re
import os
import datetime
import dateutil.tz as tz
from collections import defaultdict

class ApiManager():
    def __init__(self, path, base_dir, monitor_api=False):
        if os.path.isdir(base_dir):
            self.base_directory = os.path.abspath(base_dir)
        self._monitor_api = monitor_api
        self._parse_config_file(path)
        self.last = '' 

    def fetch(self, force=False):

        if self._check_api_status() and not force:
            print('Last time API was accessed: %s'%self.last)
            print("Current files are up to date.\nTo force process start set *force* True.")

        else:
            print(f"Fetching {len(self.endpoints)} endpoints from {self.name.upper()}")
            print(f"[{current_date('%b %d. %H:%M', tz=tz.tzlocal())}] Starting process.\n")

            # building directory tree for incoming files
            self._make_dirs()

            # fetching/storaging files
            for i, endpoint_name in enumerate(self.endpoints, 1):
                # composing url
                print(f'[{i}/{len(self.endpoints)}] Endpoint: {endpoint_name.upper()}', end=' -> ')
                endpoint_api_string = self._get_api_string(endpoint_name)
                url = self.api + endpoint_api_string

                # requesting
                print('Requesting API', end='... ')
                response = requests.get(url)

                # writing content
                filename = self._get_filename(endpoint_name)
                file_out = os.path.join(self.base_directory, endpoint_name, filename)
                with open(file_out, 'wb') as out:
                    print('Writing content\n')
                    out.write(response.content)

            self.last = current_date()
            print('Fetching files concluded.')

    def _parse_config_file(self, path):
        with open(path) as file:
            api_config = yaml.load(file, Loader=yaml.FullLoader)
            
            # renaming main api entries
            api_config = dict(map(rename_keys, api_config.items()))

            # Setting up instance name
            self.name, contents = api_config.popitem()

            # renaming possible endpoints
            if 'endpoints' in contents.keys():
                renamed_endpoints = dict(
                        map(lambda pair: rename_keys(pair), enumerate(contents['endpoints']))
                    )
                contents['endpoints'] = renamed_endpoints
            
            # Setting up instance attributes
            self.api = contents['api']
            self.endpoints = contents['endpoints']

            if self._monitor_api:
                self.status = contents['status']
    
    def _check_api_status(self):
        check = True
        if self._monitor_api:
            if '_sha1' not in dir(self):
                self._sha1 = self._make_hash()
                check = False
            else:
                check = self._sha1 == self._make_hash()
        return check

    def _make_hash(self):
        status_api = self.api + self.status['api']
        status_response = requests.get(status_api).json()
        keys = self.status['keys'].copy()
        while len(keys):
            key = keys.pop(0)
            status_response = status_response[key]
        
        return hashlib.sha1(bytes(status_response, encoding='utf-8')).hexdigest()

    def _make_dirs(self):

        for endpoint_name in self.endpoints:
            dir_path = os.path.join(self.base_directory, endpoint_name)
            os.makedirs(dir_path, exist_ok=True)
   
    def _get_api_string(self, endpoint_name):
        return self.endpoints[endpoint_name]['api']

    def _get_filename(self, endpoint_name):
        api_string = self._get_api_string(endpoint_name)
        return re.match(r".*/(.*)$", api_string).group(1)
 

class HelperApiConfig():
    """This is a helper class for *creating* a config file to be read in main ApiManager class."""

    def __init__(self, name, api):
        self.name = name
        self.api = api
        self.endpoints = []
    
    def add_status(self, **kwargs):
        self.status = kwargs
    
    def add_endpoint(self, **kwargs):
        self.endpoints.append(kwargs)
    
    def create(self, path):
        config = self._get_clean_config_dict()
        config[self.name]['api'] = self.api
        config[self.name]['endpoints'] = self.endpoints

        if hasattr(self, 'status'):
            config[self.name]['status'] = self.status
        
        with open(path, 'w') as file:
            yaml.dump(dict(config.items()), file)
    
    def _get_clean_config_dict(self):
        return defaultdict(dict)


def rename_keys(kval_pair, key='name'):
    """Utility function for changing *key* on (key, value) pairs."""

    old_key, contents = kval_pair 
    if key in contents.keys():
        new_key = contents[key]
        contents.pop(key)
    else:
        new_key = old_key

    return new_key, contents

def current_date(strftime='%A, %Y-%m-%d %T %Z', tz=tz.UTC):
    """Utility function to return formated current datetime."""

    now = datetime.datetime.now()
    return now.astimezone(tz).strftime(strftime)


# code for testing purposes
if __name__ == '__main__':
    def testing_api(covid_api):
        print('Test #1')
        covid_api.fetch() # Testing 1st use of api
        print('Test #2')
        covid_api.fetch() # Testing calling API (with updated status)
        print('Test #3')
        covid_api.fetch(force=True) # Testing Force-calling API

    name = "API-covid-tracking"
    api = "https://api.covidtracking.com"
    dir_path = "./.cache/"

    api_config = HelperApiConfig(name=name, api=api)
    api_config.add_status(api='/v1/status.json', keys=['buildTime'])
    api_config.add_endpoint(name="US-historical",
                            api="/v1/us/daily.csv")
    api_config.create(path=dir_path + "api-us-historic.yml")
    
    covid_api = ApiManager(path=dir_path + "api-us-historic.yml", base_dir='./.cache', monitor_api=True)
    testing_api(covid_api)
