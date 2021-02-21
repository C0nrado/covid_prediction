"""This script builds the traning and test sets."""

import numpy as np
import argparse
import os
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import AdaBoostRegressor
from sklearn.model_selection import GridSearchCV, cross_val_score, RepeatedKFold
from sklearn.metrics import mean_squared_error, make_scorer
from sklearn.pipeline import Pipeline
import joblib
import re

def get_class_name(estimator):
    return re.search(r".*\.([a-zA-Z]*)'>", str(estimator.__class__)).group(1)

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

parser.add_argument('--random-state',
                type=int,
                dest='random_state',
                default=42,
                help='Set random state for reproducible cross-validation results.')


args = parser.parse_args()
assert os.path.exists(args.path)

# carregando training set
X = np.load(os.path.join(args.path, 'training_set.npy'))
X_train, y_train = X[:,:-1], X[:,-1]

# montando rotina de treinamento
learning_rates = [.1, .3, .5, .7, .9]
alphas = np.logspace(-1, 5, 8)
max_boosting_iterations = 500
base_estimator = Ridge()

boosted_regr = AdaBoostRegressor(base_estimator=base_estimator,
                        n_estimators = max_boosting_iterations,
                        loss='exponential',
                        random_state=args.random_state)

# print(boosted_regr.get_params().keys())
param_grid = dict([('base_estimator__alpha', alphas),
                ('learning_rate', learning_rates)])

grid_search = GridSearchCV(boosted_regr, param_grid, verbose=1,
                    scoring=make_scorer(mean_squared_error, greater_is_better=False),
                    cv = RepeatedKFold(n_splits=4, n_repeats=5))

# otimizando hiperparametros + treinamento do modelo final
grid_search.fit(X_train, y_train)
model = grid_search.best_estimator_

if args.print:
    model_params = model.get_params()
    print('-'*50)
    print('Base Estimator: %s'%(get_class_name(model.base_estimator)))
    print('Penalty (alpha): %.4f'%model_params['base_estimator__alpha'])
    print('Cross-validation score: %.4f'%grid_search.best_score_)
    print('Boosting loss function: %s'%model.loss)
    print('Boosting learning rate: %.2f'%model.learning_rate)
    print('Boost iterations: %d'%(len(model.estimators_)))
    print('Training Error: %.1f'%(mean_squared_error(y_train, model.predict(X_train))))
    print('-'*50, '\n')

# saving model
joblib.dump(model, os.path.join(args.path, 'model.pkl'))
print('Model saved in %s'%args.path)