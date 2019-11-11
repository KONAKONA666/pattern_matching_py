import os
import sys
from typing import (
    List, Tuple, Any,
    Generic, TypeVar, Callable
)
import inspect

global_functions_dic = {}

def match(s, pattern):
    args = s["args"]
    kwargs = s["kwargs"]
    params_dict = {}
    if not len(args) + len(kwargs) == len(pattern):
        return False
    for i, param in enumerate(pattern.values()):
        annotation = param.annotation
        if annotation is param.empty:
            annotation = Any
        default = param.default
        if default is param.empty:
            default = None
        name = param.name
        if name is param.empty:
            name = i
        params_dict[name] = [default, annotation]
    is_type_matches = True
    is_value_matches = True
    print(params_dict)
    print(args)
    for s_arg, p_arg in zip(args, list(params_dict.values())[:len(args)]):
       if p_arg[1] is Any:
            is_type_matches = is_type_matches and True
       else:
            is_type_matches = is_type_matches and type(s_arg) is p_arg[1]
       if p_arg[0] is None:
            is_value_matches = is_value_matches and True
       elif is_type_matches:
            is_value_matches = is_value_matches and p_arg[0] == s_arg
       else:
            is_value_matches = False

    return is_value_matches and is_type_matches

def pm(a):
    if inspect.isfunction(a):
       sig = inspect.signature(a)
       func_name = a.__code__.co_name
       if func_name in global_functions_dic:
           global_functions_dic[func_name].append((a, sig.parameters))
       else:
           global_functions_dic[func_name] = [(a, sig.parameters)]
       def preprocess(*args, **kwargs):
           curr_args = {"args": args, "kwargs": kwargs}
           for params in global_functions_dic[func_name]:
               if match(curr_args, params[1]):
                   return params[0](*args, **kwargs)
           raise TypeError("No pattern is found")
       return preprocess
@pm
def f():
    print("void")

@pm
def f(n=1):
    print("n=1")

@pm
def f(n: int)->None:
    print(n)

f(n=0)
f(n=3)
f(1)
f()

