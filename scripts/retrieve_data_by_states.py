"""This script Configure and request API Covid-Tracking for States and retrieve its data."""

from resources.io import ApiManager, make_config
import pandas as pd
import os
import pickle
import argparse

# configurando input do script
parser = argparse.ArgumentParser(description="Configure and request API Covid-Tracking for States.")
parser.add_argument('-d', '--directory',
                type=str,
                required=True, 
                dest='base_directory',
                help='The directory used in the process.')

parser.add_argument('--export', action='store_true',
                dest='export',
                help='Flag to export api object into a pickle file.')

parser.add_argument('--file', action='store',
                type=str,
                dest='filename',
                default=None,
                help='File (+ path) to store the api object. Mandatory if export is chosen.')

args = parser.parse_args()
assert args.export and args.filename is not None
assert os.path.exists(args.base_directory)

# obtendo lista dos estados
states_list = pd.read_pickle('./data/dataframes/states_info.pkl')['state'].tolist()

# criando configuração para API (por estados)
file_name = "covid-tracking-by-states.yml"
output_dir = args.base_directory
config_path = os.path.join(output_dir, file_name)

name = "covid-tracking"
api_domain = "https://api.covidtracking.com"
fields = ['date', 'state', 'deathIncrease', 'hospitalizedIncrease', 'positiveIncrease']
status = {'api': '/v1/status.json', 'keys':['buildTime']}
endpoint_api_template = "/v1/states/%s/daily.csv"
endpoints = []

for state in states_list:
    endpoints.append({'name': state,
                'api': endpoint_api_template%(state.lower()),
                'fields': fields})

make_config(api_name = name,
        api_domain = api_domain,
        status = status,
        endpoints = endpoints,
        output_path = config_path)

# acessando a API
covid_api = ApiManager(config_path,
                    base_dir=output_dir,
                    monitor_api=True)
covid_api.fetch(force=True)

# salvando objeto api_manager
if args.export:
    with open(args.filename, 'wb') as file:
        pickle.dump(covid_api, file)