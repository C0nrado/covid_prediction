"""This script retrieves populations data from the dataset PEP provided by the census API
and stores a pandas `DataFrame` of its contents."""

from resources.io import ApiManager, make_config
import pandas as pd
import argparse

# configurando input do script
parser = argparse.ArgumentParser(description="Configure and request Census Gov API - 2019/PEP.")
parser.add_argument('--config',
                type=str,
                required=True, 
                dest='path',
                help='The yaml file path to be used.')

args = parser.parse_args()

# acessing CENSUS gov API - dataset PEP - table population
census_config_path = args.path
census_api = ApiManager(path=census_config_path, base_dir='./data')
census_api.fetch(force=True)

# formatando dataframe
endpoint_name = list(census_api.endpoints.keys())[0]
data = pd.read_json(census_api.retrieve(endpoint_name)).values

types = {'NAME':str, 'DENSITY': float, 'POP':int, 'state':int}
census_df = pd.DataFrame(data[1:], columns=data[0]).astype(types)

# salvando
out_path = './data/dataframes/census-pep-population.pkl'
census_df.to_pickle(out_path)
print('Dataframe salvo em %s.\n'%out_path)