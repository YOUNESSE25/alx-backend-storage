#!/usr/bin/env python3
'''
 Implementing an expiring web cache and tracker
 '''
import redis
import requests
from functools import wraps
from typing import Callable


redis_store = redis.Redis()


def data_cacher(method: Callable) -> Callable:
    '''
    Caches data.
    '''
    @wraps(method)
    def invoker(url) -> str:
        '''
        caching the output.
        '''
        redis_store.incr(f'count:{url}')
        res = redis_store.get(f'result:{url}')
        if res:
            return res.decode('utf-8')
        res = method(url)
        redis_store.set(f'count:{url}', 0)
        redis_store.setex(f'result:{url}', 10, res)
        return res
    return invoker


@data_cacher
def get_page(url: str) -> str:
    '''
    returns the content of a URL
    '''
    return requests.get(url).text
