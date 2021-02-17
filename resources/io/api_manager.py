"""This module implements a class for managing http api's based on custom YAML config files."""

import requests
import hashlib
import yaml
import re
import os
import datetime
import dateutil.tz as tz
from string import punctuation
from pandas import read_csv
from collections import defaultdict

class HelperApiParser():
    """This class is intended to provide private methods for parsing ApiManager
    instances input path."""
    
    def __init__(self, monitor_api):
        self.monitor_api = monitor_api

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

            if self.monitor_api:
                self.status = contents['status']
 
class HelperApiRetriever():
    """This class implements a getter in ApiManager instance."""

    def __init__(self, api_instance):
        self.api_instance = api_instance
    
    def __call__(self, endpoint_name, as_dataframe=False, **kwargs):
        instance = self.api_instance
        output_formatter = {False: str,
                            True: lambda data: read_csv(data, **kwargs)}

        if as_dataframe and instance.endpoints[endpoint_name].get('fields'):
            kwargs.update({'usecols': instance.endpoints[endpoint_name]['fields']})

        if hasattr(instance, '_sha1') or (instance.last != ''):
            output = instance.endpoints[endpoint_name]['data']
            return output_formatter[as_dataframe](output)
        else:
            return None

class ApiManager(HelperApiParser):
    def __init__(self, path, base_dir, monitor_api=False):
        HelperApiParser.__init__(self, monitor_api=monitor_api)
        assert os.path.isdir(base_dir)
        self.base_directory = os.path.abspath(base_dir)
        
        self._parse_config_file(path)
        self.retrieve = HelperApiRetriever(self)
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
                file_out = os.path.join(self.base_directory, self.name, endpoint_name, filename)
                with open(file_out, 'wb') as out:
                    print('Writing content\n')
                    out.write(response.content)

                    # storing path to endpoint data
                    self.endpoints[endpoint_name]['data'] = file_out

            self.last = current_date()
            print('Fetching files concluded.')

    def _check_api_status(self):
        check = True
        if self.monitor_api:
            if not hasattr(self, '_sha1'):
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
            dir_path = os.path.join(self.base_directory, self.name, endpoint_name)
            os.makedirs(dir_path, exist_ok=True)
   
    def _get_api_string(self, endpoint_name):
        return self.endpoints[endpoint_name]['api']

    def _get_filename(self, endpoint_name):
        api_string = self._get_api_string(endpoint_name)
        filename = re.match(r".*/(.*)$", api_string).group(1)
        if len(set(punctuation) & set(filename)) == 0 :
            return filename
        else:
            return ''.join(filter(lambda x: x.isalpha(), filename))

class HelperApiConfig():
    """This is a helper class for *creating* a config file to be read in
    main ApiManager class."""

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
        
        try: 
            with open(path, 'w') as file:
                yaml.dump(dict(config.items()), file)
                print(f"[{current_date('%b %d. %H:%M', tz=tz.tzlocal())}] Config file created for {self.name.upper()}.\n")
        
        except TypeError:
            print(f"[{current_date('%b %d. %H:%M', tz=tz.tzlocal())}] Config file for {self.name.upper()}.\n")
            print(yaml.dump(dict(config.items()), file))
    
    def _get_clean_config_dict(self):
        return defaultdict(dict)

def make_config(api_name, api_domain, output_path=None, status=None, endpoints=None):
    """This is a helper function for creating config files for ApiManager."""

    assert endpoints is not None and isinstance(endpoints, list)
    config = HelperApiConfig(name=api_name, api=api_domain)

    if status is not None:
        config.add_status(**status)
    
    for endpoint in endpoints:
        assert isinstance(endpoint, dict)
        config.add_endpoint(**endpoint)
    print("\n>>> CONFIG FILES MAKER")
    config.create(output_path)


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
# if __name__ == '__main__':
#     def testing_api(covid_api):
#         print('\n>>> Test #1: Testing API request','\n', '='*10)
#         covid_api.fetch() # Testing 1st use of api
#         print('\n>>> Test #2: Testing API monitor','\n', '='*10)
#         covid_api.fetch() # Testing calling API (with updated status)
#         print('\n>>> Test #3: Forcing api request','\n', '='*10)
#         covid_api.fetch(force=True) # Testing Force-calling API
#         print('\n>>> Test #4: Accessing endpoint data path','\n', '='*10)
#         for name in covid_api.endpoints:
#             print(covid_api.retrieve(name))
#         print('\n>>> Test #5: Retrieving DataFrame','\n', '='*10)
#         df = covid_api.retrieve(name, as_dataframe=True)
#         print(type(df))
#         print(df.head())


#     name = "api-covid-tracking"
#     api = "https://api.covidtracking.com"
#     dir_path = "./.cache/"
#     output = dir_path + 'test-api-us-historic.yml'

#     status = {'api':"/v1/status.json", 'keys':["buildTime"]}
#     endpoints = [
#         {'name':"us-historical", 'api':"/v1/us/daily.csv"},
#         {'name':"states-info", 'api':"/v1/states/info.csv", 'fields':['state', 'name', 'notes']}
#     ]
    
#     make_config(api_name = name,
#                 api_domain = api,
#                 status=status,
#                 endpoints=endpoints,
#                 output_path=output)
    

#     covid_api = ApiManager(path=dir_path + "test-api-us-historic.yml", base_dir='./.cache', monitor_api=True)
#     testing_api(covid_api)