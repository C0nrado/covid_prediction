"""This script evaluates the trained model."""

import os
import joblib
import numpy as np
import argparse
import sklearn.metrics as metrics

# configurando input do script
parser = argparse.ArgumentParser(description="Evaluate a trained model in the test set.")

parser.add_argument('-d', '--directory',
                type=str,
                dest='path',
                default='./data',
                help='Directory where to look for model and test set.')

parser.add_argument('--metric',
                type=str,
                dest='metric',
                default='mean_squared_error',
                help='Print the chosen evaluation metric value as in scikit-learn metrics module.')

parser.add_argument('--boosting-steps',
                action='store_true',
                dest='boosting_steps',
                help='Dump the evaluation metric for each boosting step.')

parser.add_argument('--dry',
                action='store_true',
                dest='dry_run',
                help='Make a dry run of the script.')


args = parser.parse_args()
assert os.path.exists(args.path)

# Setting metric for evaluation
eval_metric = getattr(metrics, args.metric)
print('Evaluation metric: %s'%args.metric)

# loading test set
test_set_path = os.path.join(args.path, 'test_set.npy')
test_set = np.load(test_set_path)
X_test, y_test = test_set[:, :-1], test_set[:, -1]
print('Test set size: %d'%len(test_set))

# Loading trained model
model_path = os.path.join(args.path, 'model.pkl')
model = joblib.load(model_path)

# Evaluating model
y_pred = model.predict(X_test)
eval_value = eval_metric(y_test, y_pred)
print('Evaluation value: %.2f'%eval_value)
print('Variance in test set: %.2f'%(np.var(y_test)))

# Dumping prediction
if not args.dry_run:
    np.save(os.path.join(args.path, 'y_pred.npy'), y_pred)
    print('Predictions on test set saved.')

if args.boosting_steps and not args.dry_run:
    y_preds = model.staged_predict(X_test)
    eval_steps = map(lambda y: eval_metric(y_test, y), y_preds)
    np.save(os.path.join(args.path, 'eval_boosting_steps.npy'), list(eval_steps))
    print('Evaluated boosting iterations (steps) saved.')