from elixirjiznypy import pm

@pm
def f(n=0):
    return 1
@pm
def f(n=1):
    return 1

@pm
def f(n: int)->int:
    return f(n-1) + f(n-2)

if __name__ == "__main__":
    print(f(10))
