"""
This module contains utility functions for functional programming.

Functional Toolkit is a module with a set of functions intended to
deliver a more flexible option for writing functional code in python
in addition to built-in functions and the `functools` built-in module.
It currently offers functions providing *currying* and *composing*.
"""

from inspect import signature
from functools import partial

def curry(func):
    """This function returns a curried *func*

    This function receives a python function as a single argument and
    returns a curried version allowing partial applications on itself
    recursively.
    The curried function will *only* be evaluated after all arguments
    are provided. The method for providing inputs/arguments in the
    curried function is the same as in an ordinary python function,
    i.e., positional inputs as in the function declaretion, or as
    kwargs.

    OBS: Same restrictions in feeding arguments to functions in pythons
    will apply for curried functions.

    Parameters
    ----------

    func:
        An ordinary python function

    Returns
    -------
        A new function suitable for partial application

    Exemples
    --------

    def f(a,b): return a+b

    curried_f = curry(f)
    sum_5 = curried_f(5) # a = 5
    sum_5(2) # b = 2
    > 7

    sum_5 = curried_f(a=5)
    sum_5(2) # This won't work for 'a' is a positional argument
    sum_5(b=2) # This works just fine!
    > 7
    """

    def curried(*args, func=func, **kwargs):
        # dictionary of <param>:<default value>
        func_params = signature(func).parameters 

        # a dictionary of parameters in *func_parame* set as kwargs
        kwargs_func = dict(filter(lambda x: x[1].default != x[1].empty, func_params.items()))

        # counting the unset parameters in * func_params*
        n_args_remaining = len(func_params) - len(kwargs_func)

        # count positional parameters feed to the function
        n_args_input = len(args) 
        # count parameters set as kwargs
        n_kwargs_input = len(set(kwargs.keys()) - set(kwargs_func.keys()))

        if n_args_remaining <= n_args_input + n_kwargs_input:
            return func(*args, **kwargs)
        else:
            func = partial(func, *args, **kwargs)
            return curry(func)
    return curried

def compose(*functions):
    """This function makes a composition of functions.

    The composition of functions works as a single pipeline where each
    function receives as input the output frm the previous in the
    sequence.
    The sequence runs from right -> left according to the order in which
    the *functions* were provided.
    It is required that *funcitons* are all pure functions, they
    receives only one argument as input the spits out only one
    output.

    Parameters
    ----------

    functions:
        A tuple of python functions (order matters).

    Return
    ------
        A pure function.

    Exemple
    -------

    pipeline = copmose(lambda x:x+10, lambda x: x*2)
    process = map(pipline, [1,2,3])
    list(process)
    > [12, 14, 16]
    """

    def composed(functions, arg):
        # runs through every function until the last in the sequence.
        if len(functions) == 1:
            return functions[0](arg)
        else:
            func = functions[-1]
            arg = func(arg)
            return composed(functions[:-1], arg)
    return partial(composed, functions)