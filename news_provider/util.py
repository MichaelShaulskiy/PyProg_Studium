from typing import List, Optional, Iterable, Iterator, Callable
import requests
from pprint import pprint
from dataclasses import dataclass
import sqlite3
import hashlib

def cacheenabledressource():
    """
    Apply this decorator to have a webresource cached
    Lookups a ressource in the database and if it isn't stale
    returns it without doing the request
    """
    db_connection = sqlite3.connect("News.db")

    def decorator(func):
        orig_get = requests.get
        def patched_get(*args, **kwargs):
            """
            Returns a requests.Response object without performing a web request
            if the resource is found in the db
            """
            url: str = args[0]
            thehash = hashlib.sha256(url.encode("utf-8"))
            cursor = db_connection.cursor()
            cursor.execute(f"SELECT raw_article FROM NewsArticles WHERE hash = '{thehash.hexdigest()}' LIMIT 1;")
            result = cursor.fetchone()

            if result:
                response = requests.Response()
                response.status_code = 200
                response._content = result[0].encode("utf-8")
                response.url = f"{args[0]}"
                response.encoding = "utf-8"
                response.reason = "OK"
                return response
            else:
                # get the resource and put it into the database
                response = orig_get(*args, **kwargs)
                cursor.execute(f"""
                               INSERT INTO NewsArticles (raw_article, hash)
                               VALUES (?, ?);""",
                               (response.text, thehash.hexdigest()))
                db_connection.commit()
                return response

        def wrapper(*args, **kwargs):
            # look up if we have the resource cached
            orig_get = requests.get
            requests.get = patched_get
            ret_func = func(*args, **kwargs)
            requests.get = orig_get
            return ret_func
        return wrapper
    return decorator

class NewsUtil(object):

    def __init__(self):
        assert False, "Don't construct NewsUtil"

    @staticmethod
    @cacheenabledressource()
    def fetch_source(url: str) -> Optional[str]:
        def __inner_try(url: str) -> str:
            res = requests.get(url)
            res.raise_for_status()
            return res.text
        try:
            res = __inner_try(url)
            return res
        except requests.HTTPError as e:
            print(str(e))

        return ""
    
    @staticmethod
    def new_news_provider():
        pass

if __name__ == "__main__":
    ARTICLES = ["https://www.welt.de/politik/deutschland/article256033536/Machtwechsel-Linnemann-gibt-100-Tage-Versprechen-Welche-Massnahmen-die-CDU-sofort-umsetzen-will.html",
                "https://www.welt.de/politik/deutschland/article256021072/To-go-Behaelter-aus-Plastik-Warum-Steuern-und-Abgaben-gegen-die-Flut-des-Einweg-Muells-nicht-ankommen.html",
                "https://www.welt.de/iconist/essen-und-trinken/article256029568/Sternekoeche-Wie-nachhaltig-und-fair-geht-es-in-der-Spitzengastronomie-wirklich-zu.html"]
    
    for art in ARTICLES:
        weltcnt = NewsUtil.fetch_source(art)
        pprint(weltcnt)