"""This script builds the traning and test sets."""

import numpy as np
import argparse
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import joblib

# configurando input do script
parser = argparse.ArgumentParser(description="Train a model.")

parser.add_argument('-d', '--directory',
                type=str,
                dest='path',
                default='./data',
                help='Directory where to look for training set.')

parser.add_argument('--print',
                action='store_true',
                dest='print',
                help='Flag the script print model metrics.')

args = parser.parse_args()
assert os.path.exists(args.path)

# carregando training set
X = np.load(os.path.join(args.path, 'training_set.npy'))
X_train, y_train = X[:,:-1], X[:,-1]

# montando rotina de treinamento
model = LinearRegression().fit(X_train, y=y_train)

# # saving model
joblib.dump(model, os.path.join(args.path, 'model.pkl'))
print('Model saved in %s'%args.path)