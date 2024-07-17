#!/usr/bin/env python3
"""
redis class and methods
"""
import redis
from uuid import uuid4
from functools import wraps
from typing import Union, Callable, Optional


def count_calls(method: Callable) -> Callable:
    '''count how many times methods of Cache class are called'''
    key = method.__qualname__

    @wraps(method)
    def Wrapper(self, *args, **kwargs):
        '''return the Wrapper'''
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return Wrapper


def call_history(method: Callable) -> Callable:
    ''' store the history of inputs and outputs'''
    @wraps(method)
    def Wrapper(self, *args, **kwargs):
        '''wrap the decorated function and return the Wrapper'''
        input = str(args)
        self._redis.rpush(method.__qualname__ + ":inputs", input)
        output = str(method(self, *args, **kwargs))
        self._redis.rpush(method.__qualname__ + ":outputs", output)
        return output
    return Wrapper


def replay(fn: Callable):
    ''' display the history of calls'''
    R = redis.Redis()
    func_name = fn.__qualname__
    c = R.get(func_name)
    try:
        c = int(c.decode("utf-8"))
    except Exception:
        c = 0
    print("{} was called {} times:".format(func_name, c))
    inputs = R.lrange("{}:inputs".format(func_name), 0, -1)
    outputs = R.lrange("{}:outputs".format(func_name), 0, -1)
    for inp, outp in zip(inputs, outputs):
        try:
            inp = inp.decode("utf-8")
        except Exception:
            inp = ""
        try:
            outp = outp.decode("utf-8")
        except Exception:
            outp = ""
        print("{}(*{}) -> {}".format(func_name, inp, outp))


class Cache:
    ''' declares a Cache redis class'''
    def __init__(self):
        '''upon init to store an instance and flush'''
        self._redis = redis.Redis(host='localhost', port=6379, db=0)
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        ''' returns a string'''
        rkey = str(uuid4())
        self._redis.set(rkey, data)
        return rkey

    def get(self, key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        ''' convert the data back to the desired format'''
        Value = self._redis.get(key)
        if fn:
            Value = fn(Value)
        return Value

    def get_str(self, key: str) -> str:
        ''' parametrize Cache.get with correct conversion function'''
        Value = self._redis.get(key)
        return Value.decode("utf-8")

    def get_int(self, key: str) -> int:
        ''' parametrize Cache.get with correct conversion function'''
        Value = self._redis.get(key)
        try:
            Value = int(Value.decode("utf-8"))
        except Exception:
            Value = 0
        return Value
