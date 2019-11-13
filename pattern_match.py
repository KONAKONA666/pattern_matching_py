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
    def __eq__(self, a):
        return True

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
    def __init__(self, name: str, value: Any, annotation: Any)->None:
        self.name = self.process_name(name)
        self.value = self.process_value(value)
        self.annotation = self.process_annotation(annotation)

    def process_annotation(self, annotation)->Any:
        if annotation is inspect._empty:
            return type(self.value) if not isinstance(self.value, EmptyDefaultValue) else Any
        if PatternTerm.is_generic(annotation):
            return PatternTerm.process_generic(annotation)
        if PatternTerm.is_class(annotation):
            return annotation
        if PatternTerm.is_type(annotation):
            return annotation
        if annotation is Any:
            return annotation

    def process_value(self, value: Any)->Any:
        if value is inspect._empty:
            return EmptyDefaultValue()
        else:
            return value

    def process_name(self, name: str)->str:
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
        #print("Name check: {0}\nType Check: {0}\nValue Check: {0}".format(self.check_name))
        return self.check_name(pattern_term.name) and self.check_annotation(pattern_term.annotation) and self.check_value(pattern_term.value)
    def check_name(self, name: str)->bool:
        return self.name == "" or self.name == name
    def check_value(self, value: Any)->bool:
        return isinstance(value, EmptyDefaultValue) or isinstance(self.value, EmptyDefaultValue) or self.value == value
    def check_annotation(self, annotation):
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
    args_pattern_term = PatternTerm("args", EmptyDefaultValue(), Any)
    kwargs_pattern_term = PatternTerm("kwargs", EmptyDefaultValue(), Any)
    def __init__(self, *args, **kwargs):
        self.args = [("", arg, type(arg)) for arg in args]
        self.kwargs = [(key, kwargs[key][0], kwargs[key][1]) for key in kwargs]
        processed_args = self.args + self.kwargs
        self.pattern_terms = [PatternTerm(*arg) for arg in processed_args]
    def __eq__(self, pattern: 'Pattern')->False:
        if len(self) < len(pattern):
            return False
        if Pattern.args_pattern_term in pattern.pattern_terms:
            print(self)
            if len(pattern.pattern_terms) > len(self.args):
                return False
            idx =  pattern.pattern_terms.index(Pattern.args_pattern_term)
            return self.pattern_terms[:idx] == pattern.pattern_terms[:idx]
        print(self)
        print(pattern)
        return self.pattern_terms[:len(self.args)] == pattern.pattern_terms[:len(self.args)] and \
                all([lpattern_term in pattern.pattern_terms[len(self.args):] for lpattern_term in self.pattern_terms[len(self.args):]]+[True])
    def __str__(self)->str:
        return "<Pattern: ["+",".join([str(term) for term in self.pattern_terms])+"]>"
    def __len__(self)->int:
        return len(self.pattern_terms)

pattern_mapper = PatternMapper()
def match_parameters(name: str)->Callable: 
    def __match_parameters(*args, **kwargs)->Any:
        processed_kwargs = {key: (kwargs[key], type(kwargs[key])) for key in kwargs}
        curr_pattern = Pattern(*args, **processed_kwargs)
        patterns = pattern_mapper[name]
        matched = list(filter(lambda x: curr_pattern == x["pattern"], patterns))
        if False and len(matched)>1:
            raise MultipleMatchError("{0} corresponds to {1} matches".format(curr_pattern, len(matched)))
        elif not len(matched):
            raise NoMatchError("{0} mathches with no pattern".format(curr_pattern))
        else:
        #    print(matched[0]["pattern"])
            return matched[0]["func"](*args, **kwargs)
    return __match_parameters

def pm(func):
    name = PatternMapper.get_name(func)
    pattern = Pattern(**PatternMapper.get_params(func))
    #print(pattern)
    pattern_mapper.add_pattern(name, pattern, func)
    return match_parameters(name)


class P:
    pass

@pm
def f(a: P):
    print(1)

@pm
def f(a=1, b=1, c=2, d=3, *args):
    print(args)
    return 1

print(f(1, 0, 2, 3, 4, 5, 6))

