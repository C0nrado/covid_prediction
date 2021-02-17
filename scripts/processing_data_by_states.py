"""This script prepares the data for clustering."""

from resources.io import ApiManager, make_config
from resources.processing import DataframeTransformer
import pandas as pd
import os
import pickle
import argparse
import numpy as np

# configurando input do script
parser = argparse.ArgumentParser(description="Perform the processing of states data for further deeper analysis.")
parser.add_argument('-i', '--input',
                type=str,
                required=True, 
                dest='api_path',
                help='The input path for api manager object.')

parser.add_argument('-o', '--output', 
                dest='output',
                default='./dataframes',
                help='Output directory for dumping processed data.')

parser.add_argument('--consume', action='store_true',
                help='Flag for deleting files after consumed.')

args = parser.parse_args()
assert os.path.exists(args.api_path)
assert os.path.exists(args.output)

# Recuperando o objeto api_manager
with open(args.api_path, 'rb') as api_file:
    covid_api = pickle.load(api_file)

# Configurando pipeline
steps = [('convert_date_to_index', None),
        ('filling_period_index', None),
        ('slice_dataframe', dict(start='apr-2020', stop='nov-2020')),
        ('select_features', dict(features=['state', 'deathIncrease'])),
        ('groupby_feature', dict(by='state', feature='deathIncrease', agg_func=np.array))]

pipeline = DataframeTransformer(steps=steps)

# processing states dataframes
states_list = list(covid_api.endpoints.keys())
states_map = map(lambda state: pipeline(covid_api.retrieve(state, as_dataframe=True)), states_list)
states_dataframe = pd.concat(list(states_map)) \
                        .pipe(pd.DataFrame)

# aggregating other fields (fips , population & density)"""This script prepares the data for clustering."""

from resources.io import ApiManager, make_config
from resources.processing import DataframeTransformer
import pandas as pd
import os
import pickle
import argparse
import numpy as np

# configurando input do script
parser = argparse.ArgumentParser(description="Perform the processing of states data for further deeper analysis.")
parser.add_argument('-i', '--input',
                type=str,
                required=True, 
                dest='api_path',
                help='The input path for api manager object.')

parser.add_argument('-o', '--output', 
                dest='output',
                default='./data/dataframes',
                help='Output directory for dumping processed data.')

parser.add_argument('--file',
                dest='file',
                required=True,
                help='Filename for dumping data.')

parser.add_argument('--consume', action='store_true',
                help='Flag for deleting files after consumed.')

args = parser.parse_args()
assert os.path.exists(args.api_path)
assert os.path.exists(args.output)

# Recuperando o objeto api_manager
with open(args.api_path, 'rb') as api_file:
    covid_api = pickle.load(api_file)

# Configurando pipeline
steps = [('convert_date_to_index', None),
        ('filling_period_index', None),
        ('slice_dataframe', dict(start='apr-2020', stop='nov-2020')),
        ('select_features', dict(features=['state', 'deathIncrease'])),
        ('groupby_feature', dict(by='state', feature='deathIncrease', agg_func=np.array))]

pipeline = DataframeTransformer(steps=steps)

# processing states dataframes
states_list = list(covid_api.endpoints.keys())
states_map = map(lambda state: pipeline(covid_api.retrieve(state, as_dataframe=True)), states_list)
states_dataframe = pd.concat(list(states_map)) \
                        .pipe(pd.DataFrame) \
                        .reset_index()

#  agregando dados de outros fontes (população e densidade)
info_dataframe = pd.read_pickle('./data/dataframes/states_info.pkl').drop('notes', axis=1)
census_dataframe = pd.read_pickle('./data/dataframes/census-pep-population.pkl').rename({'state':'fips'}, axis=1)
df = pd.merge(states_dataframe, info_dataframe, on='state')
df = pd.merge(df, census_dataframe, on='fips')

# dumping dataframe final
output = os.path.join(args.output, args.file)
df.drop('NAME', axis=1) \
    .rename({'POP':'population', 'DENSITY':'denisty'}, axis=1) \
    .to_pickle(os.path.join(output))
print('Data processed and dumped at %s.\n'%output)