#!/usr/bin/python3
    
def memo(func):
    d = {}
    def wrapp(*args):
        if args not in d:
            d[args] = func(*args)
        return d[args]
    return wrapp

def fmemo(func, *args):
    @memo
    def wrapp(*args):
        return func(*args)
    
    return wrapp(*args)

# @memo
def fib(n):
    if n < 2:
        return n
    else:
        return fib(n-1) + fib(n-2)

if __name__ == "__main__":
    print(fmemo(fib, 7))

    

