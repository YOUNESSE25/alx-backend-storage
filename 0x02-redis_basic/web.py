#!/usr/bin/env python3
"""
Implementing an expiring web cache and tracker
"""
import redis
import requests
from functools import wraps

store = redis.Redis()


def count_url_access(method):
    """
    decorator counting many times
    a URL is accessed 
    """
    @wraps(method)
    def wrapper(url):
        CachedKey = "cached:" + url
        CachedData = store.get(CachedKey)
        if CachedData:
            return CachedData.decode("utf-8")

        countKey = "count:" + url
        html = method(url)

        store.incr(countKey)
        store.set(CachedKey, html)
        store.expire(CachedKey, 10)
        return html
    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """
    returns HTML content of a url
    """
    res = requests.get(url)
    return res.text
