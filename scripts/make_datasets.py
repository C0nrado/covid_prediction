"""This script builds the traning and test sets."""

from resources.processing import DataframeTransformer
from statsmodels.tsa.api import ExponentialSmoothing
from resources.utils import curry
import pandas as pd
import numpy as np
import os
import argparse

# configurando input do script
parser = argparse.ArgumentParser(description="Builds the training and test sets for machinel learning.")
parser.add_argument('-d', '--directory',
                type=str,
                dest='path',
                default='./data',
                help='The directory to dump the sets.')

parser.add_argument('--keep',
                action='store_true',
                dest='keep',
                help='Flag the script to not dump the files.')

args = parser.parse_args()
assert os.path.exists(args.path)

print('[BUILDING DATASETS] Starting process...')

# Carregando dataframes
input_df = pd.read_pickle('./data/dataframes/us_historical.pkl')

# Preparando transformações
features = ['positiveIncrease', 'hospitalizedIncrease']
target = ['deathIncrease']
steps = [('convert_date_to_index', None),
         ('filling_period_index', None),
         ('select_features', dict(features=features + target)),
         ('slice_dataframe', dict(start='jun-2020', stop='dec-2020')),
         ('smoothen', dict(period=7, seasonal=7))]

print('[BUILDING DATASETS] Applying transformations...')
pipeline = DataframeTransformer(steps=steps)
df = pipeline(input_df)

# Preparando dataset
test_period = 'dec-2020'
positiveIncrease_shift = 31
hospitalizedIncrease_shift = 10
dataset = df.apply({'positiveIncrease': lambda col: col.shift(positiveIncrease_shift),
            'hospitalizedIncrease': lambda col: col.shift(hospitalizedIncrease_shift)}).dropna()


dataset = dataset.join(df[target])
filter_period = dataset.index > test_period
training_set = dataset[~filter_period].values
test_set = dataset[filter_period].values

print('[BUILDING DATASETS] Finished process.')

if not args.keep:
    np.save(os.path.join(args.path, 'training_set.npy'), training_set)
    np.save(os.path.join(args.path, 'test_set.npy'), test_set)
    print('Files dumped.\n')