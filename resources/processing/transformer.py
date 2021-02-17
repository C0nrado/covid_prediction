"""This module contains class containers of custom methods for pandas `DataFrame` objects."""

import pandas as pd
from resources.io import ApiManager
from resources.utils import compose, curry
from statsmodels.tsa.api import STL

import os
print(os.getcwd())
class Piper():
    def __init__(self, steps):
        assert isinstance(steps, list)
        self.steps = steps
        self._preprocessing()

    def _preprocessing(self):
        self.steps = list(map(lambda step: (step[0], {} if self.check_step(step) else step[1]), self.steps))

    @staticmethod
    def check_step(step):
        assert isinstance(step, tuple)
        assert isinstance(step[0], str)
        assert len(step) == 2

        return (len(step) == 1) or (step[1] is None)
    
    # def __call__(self, df))

class DataframeCustomMethods():
    """This is class is only a container for a set to custom pandas `DataFrame` methods.""" 

    @staticmethod
    def convert_date_to_index(df):
        df = df.assign(date = df['date'].apply(pd.Period)) \
                .set_index('date').sort_index(ascending=True)
        return df
    
    @staticmethod
    def filling_period_index(df):
        if not missing_period(df.index):
            return df
        else:
            new_index = pd.period_range(start=df.index[0], end=df.index[-1], freq=df.index.freq)
            return df.reindex(new_index)
    
    @staticmethod
    def slice_dataframe(df, start, stop, step=None):
        slice_obj = slice(start, stop, step)
        return df.loc[start:stop]
    
    @staticmethod
    def select_features(df, features):
        return df.loc[:,features]
    
    @staticmethod
    def groupby_feature(df, by, agg_func, feature):
        return df.groupby(by=by)[feature].apply(agg_func)
    
    @staticmethod
    def apply_func(df, func):
        print(type(func))
        return df.apply(func)

    @staticmethod
    def smoothen(df, period, seasonal):
        smoother = lambda endog: STL(endog, period=period, seasonal=seasonal).fit().trend
        return df.apply(smoother, axis=0)

class DataframeTransformer(Piper, DataframeCustomMethods):
    def __init__(self, steps):
        Piper.__init__(self, steps=steps)
        assert all(hasattr(self, name) for name, _ in self.steps)
        names, kwargs_list = zip(*steps)
        curried_functions = list(map(lambda name: curry(getattr(self, name)), names))
        self.steps = [curried_function(**kwargs) if kwargs is not None else curried_function
                                for curried_function, kwargs in zip(curried_functions, kwargs_list)][::-1]

    def __call__(self, df):
        pipeline = compose(*self.steps)
        return pipeline(df)
    
def missing_period(period_index):
    full_index = pd.period_range(start=period_index[0], end=period_index[-1], freq=period_index.freq)
    return ~len(full_index) == len(period_index)
