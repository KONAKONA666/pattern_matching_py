# ElixirJizniPy is a Pattern Matching lib for python

ElixirJizniPy is small lib, inspired by Elixir pattern matching concept 

## How it works ?

```python
from elixirjiznypy import pm

@pm
def your_function(here_is_arguments_as_pattern):
  ....
#another one
@pm
def your_function(here_is_arguments_as_pattern):
  ....
#and another one
@pm
def your_function(here_is_arguments_as_pattern):
  ....
#here we go
@pm
def your_function(here_is_arguments_as_pattern):
  ....
```

## Some examples
When you have to deal with states in function, pattern mathcing is right choice. In fact function is class, consequantly you can generate functions with patterns map(pm, functions), where you function.__name__="some_common_name" in fuinctions and dont forget to make a signature with inspect! May be I'll show it, may be not, idk. 

```python
#Natürlich we are gonna write fibonacci sequence

@pm
def fib(n:int=0)->int:
    return 1
@pm
def fib(n:int=1)->int:
    return 1
@pm
def fib(n:int)->int:
    return fib(n-1)+f(n-2)

fib(10)

#it worls really good with recursion(dynamical programming for example) and switch cases

def edit_distance(s1: string, s2: string):
    def some_distance(u, v)->int:
        ......
        
    @pm
    def _edit_distance(i:int=0, j:int=0)-int:
        return 0
    @pm
    def _edit_distance(i:int=0, j:int)->int:
        return i
    @pm
    def _edit_distance(i:int, j:int=0)->int:
        return j
    @pm
    def _edit_distance(i:int, j:int)->int:
        return min(_edit_distance(i, j-1)+1, _edit_distance(i-1, j)+1, _edit_distance(i-1, j-1)+some_distance(s1[i], s2[j]))
    
    return _edit_distance(len(s1)-1, len(s2)-1)
 ```
## Available Patterns, Yeah!

```python
@pm
def f(x:type|class|,......) #typed pos args
```
When, there is no match value(default) pm matches with type, if no type and no value is angegeben it matches with argument 
```python
@pm
def f(x:int=1, y:str="pidoras") #valued
```
When, there is no type pm takes type(value) as type(annotation)
```python
@pm
def f(a, b, c, *args) #prefix match
```
Hoba!
```python
@pm
def f(a=[1, EmptyDefaultValue(), 3, EmptyDefaultValue()])
```
EmplyDefaultValue means it can be any value __eq__->True for every arguments(pure function kstati), yeap it is instance, i have Singelton, but idk, next commit!

And something more......

## Tasks

- ~~firstcommit!~~
- ~~refactor~~
- add conditional patterns
- add Generics
- add regexp
- add ~~machine learning and blockchlen~~ SWITCH OPERATOR FOR PYTHON!
- **COVER WITH TESTS** SUPER IMPORTANT 
- CI/CD and so on....






