from typing import List, Optional, Iterable, Iterator, Callable
import requests
from pprint import pprint

def cacheenabledressource(func):
    """
    Apply this decorator to have a webresource cached
    Lookups a ressource in the database and if it isn't stale
    returns it without doing the request
    """
    def wrapper():
        assert False, "Not yet implemented"
    return wrapper

class NewsUtil(object):

    def __init__(self):
        assert False, "Don't construct NewsUtil"

    @staticmethod
    def fetch_source(url: str) -> Optional[str]:
        def __inner_try(url: str) -> str:
            res = requests.get(url)
            res.raise_for_status()
            return res.text
        try:
            res = __inner_try(url)
            pprint(res)
            return res
        except:
            print("fetch failed")

        return ""
    
    @staticmethod
    def new_news_provider():
        pass