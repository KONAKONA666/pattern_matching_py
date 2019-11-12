import os
import sys
from typing import (
    List, Tuple, Any,
    Generic, TypeVar, Callable, GenericMeta
)
import inspect

from collections import OrderedDict
from inspect import Parameter

class EmptyDefaultValue:
    pass

class NoMatchError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class MultipleMatchError(Exception):
    def __init__(self, msg):
        super().__init__(msg)

class PatternMapper:
    def __init__(self):
        self.func_dict = {}
    def __getitem__(self, key: str)->OrderedDict:
        return self.func_dict[key]
    def __setitem__(self, key: str, value: OrderedDict)->None:
        self.func_dict[key] = value
    def add_pattern(self, name: str, pattern: 'Pattern', func):
        if not name in self.func_dict:
            self[name] = []
        self[name].append({"func": func, "pattern": pattern})
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(PatternMapper, cls).__new__(cls)
        return cls.instance
    @staticmethod
    def get_name(func):
        return func.__code__.co_name
    @staticmethod
    def get_params(func):
        s = inspect.signature(func)
        return OrderedDict([(param, (s.parameters[param].default, s.parameters[param].annotation)) for param in s.parameters])

class PatternTerm(object):
    def __init__(self, name: str, value: Any, annotation: Any):
        self.name = PatternTerm.process_name(name)
        self.value = PatternTerm.process_value(value)
        self.annotation = PatternTerm.process_annotation(annotation)
    @staticmethod
    def process_annotation(annotation: Any):
        if annotation is inspect._empty:
            return Any
        if PatternTerm.is_generic(annotation):
            return PatternTerm.process_generic(annotation)
        if PatternTerm.is_class(annotation):
            return annotation
        if PatternTerm.is_type(annotation):
            return annotation
        if annotation is Any:
            return annotation
    @staticmethod
    def process_value(value: Any):
        if value is inspect._empty:
            return EmptyDefaultValue()
        else:
            return value
    @staticmethod
    def process_name(name: str)->str:
        return name
    @staticmethod
    def is_generic(annotation: Any)->bool:
        return isinstance(annotation, GenericMeta)
    @staticmethod
    def is_class(annotaion: Any)->bool:
        return isinstance(annotaion.__class__,  type)
    @staticmethod
    def is_type(annotaion: Any)->bool:
        return isinstance(annotation, type)

    def __eq__(self, pattern_term: 'PatternTerm')->bool:
        return self.check_name(pattern_term.name) and self.check_annotation(pattern_term.annotation) and self.check_value(pattern_term.value)
    def check_name(self, name: str)->bool:
        return self.name == "" or self.name == name
    def check_value(self, value: Any)->bool:
        return isinstance(value, EmptyDefaultValue)or isinstance(self.value, EmptyDefaultValue) or self.value == value
    def check_annotation(self, annotation: Any):
        if annotation is Any:
            return True
        if PatternTerm.is_generic(annotation):
           return self.match_generic(annotaion)
        if PatternTerm.is_class(annotation):
            return self.annotation is annotation
        if PatternTerm.is_type(annotation):
            return self.annotation is annotaion
    def match_generic(self, annotation):
        return False
    def __str__(self):
        return "({0}, {1}, {2})".format(self.name, self.value, self.annotation)


class Pattern(object):
    def __init__(self, *args, **kwargs):
        processed_args = [("", arg, type(arg)) for arg in args] + [(key, kwargs[key][0], kwargs[key][1]) for key in kwargs]
        self.pattern_terms = [PatternTerm(*arg) for arg in processed_args]
    def __eq__(self, pattern: 'Pattern'):
        return self.pattern_terms == pattern.pattern_terms
    def __str__(self):
        return "<Pattern: ["+",".join([str(term) for term in self.pattern_terms])+"]>"
    def __len__(self):
        return len(self.pattern_terms)

pattern_mapper = PatternMapper()
def match_parameters(name: str): 
    def __match_parameters( *args, **kwargs):
        processed_kwargs = {key: (kwargs[key], type(kwargs[key])) for key in kwargs}
        curr_pattern = Pattern(*args, **processed_kwargs)
        patterns = pattern_mapper[name]
        matched = list(filter(lambda x: curr_pattern == x["pattern"], patterns))
        if False and len(matched)>1:
            raise MultipleMatchError("{0} corresponds to {1} matches".format(curr_pattern, len(matched)))
        elif not len(matched):
            raise NoMatchError("{0} mathches with no pattern".format(curr_pattern))
        else:
            return matched[0]["func"](*args, **kwargs)
    return __match_parameters

def pm(func):
    name = PatternMapper.get_name(func)
    pattern = Pattern(**PatternMapper.get_params(func))
    pattern_mapper.add_pattern(name, pattern, func)
    return match_parameters(name)



@pm
def f(n:int=1)->int:
    return 1

@pm
def f(n:int=2):
    return 1

@pm
def f(n: int):
    return f(n-1)+f(n-2)

print(f(11))
