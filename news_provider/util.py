from typing import List, Optional, Iterable, Iterator, Callable
import requests
from pprint import pprint
from dataclasses import dataclass
import sqlite3

def cacheenabledressource(resource):
    """
    Apply this decorator to have a webresource cached
    Lookups a ressource in the database and if it isn't stale
    returns it without doing the request
    """
    def decorator(func):
        def patched_get(*args, **kwargs):
            """
            Returns a requests.Response object without performing a web request
            if the resource is found in the db
            """
            response = requests.Response()
            response.status_code = 200
            response._content = b"Wrapper"
            response.url = "https://test.de"
            response.encoding = "utf-8"
            response.reason = "OK"
            return response

        def wrapper(*args, **kwargs):
            # look up if we have the resource cached
            orig_get = requests.get
            requests.get = patched_get
            ret_func = func(*args, **kwargs)
            requests.get = orig_get
        return wrapper
    return decorator

class NewsUtil(object):

    def __init__(self):
        assert False, "Don't construct NewsUtil"

    @staticmethod
    @cacheenabledressource("welt")
    def fetch_source(url: str) -> Optional[str]:
        def __inner_try(url: str) -> str:
            res = requests.get(url)
            res.raise_for_status()
            return res.text
        try:
            res = __inner_try(url)
            pprint(res)
            return res
        except requests.HTTPError as e:
            print(str(e))

        return ""
    
    @staticmethod
    def new_news_provider():
        pass

if __name__ == "__main__":
    weltcnt = NewsUtil.fetch_source("https://welt.de")
    pprint(weltcnt)