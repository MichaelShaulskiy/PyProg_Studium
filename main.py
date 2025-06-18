import requests
from pprint import pprint
from openai import OpenAI
import openai
import os
from typing import List, Tuple, Optional, Any
from bs4 import BeautifulSoup
import sqlite3
import time
from PySide6.QtCore import QObject, Signal, Slot, QCoreApplication
from news_provider.rssparser import RSSItem, RSS
from news_provider.provider import NewsSite, NewsSourceIndex


NEWS_SITES = []
NEWS_SOURCES = [
    {
        "name": "Tagesschau",
        "url": "https://www.tagesschau.de/index~rss2.xml"
    },
    {
        "name": "Welt",
        "url": "https://www.welt.de/?service=Rss"
    },
    {
        "name": "SZ",
        "url": "https://rss.sueddeutsche.de/rss/Topthemen"
    },
    {
        "name": "Spiegel",
        "url": "https://www.spiegel.de/schlagzeilen/tops/index.rss"
    }
] 

# TODO: Kann die erstellung einer sqllite db überhaupt fehlschlagen?
# Error handling betreiben wenn ja
def setup_db():
    with sqlite3.connect("News.db") as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS NewsSources (source_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT, last_queried INTEGER, rss_content TEXT, hash TEXT);")
        cursor.execute("""CREATE TABLE IF NOT EXISTS NewsArticles (
                        article_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        source_id INTEGER,
                        title TEXT,
                        author TEXT,
                        article_text TEXT,
                        raw_article TEXT,
                        category TEXT,
                        timestamp INTEGER,
                        reading_time INTEGER,
                        subscription INTEGER,
                        hash TEXT,
                        FOREIGN KEY (source_id) REFERENCES NewsSources (source_id));""")
        conn.commit()

def initial_rss_fetch():
    with sqlite3.connect("News.db") as conn:
        cursor = conn.cursor()

def fetch_with_retry(url, times=5, timeout=1000):
    for curr in range(0, times):
        try:
            ret = requests.get(url)
            ret.raise_for_status()
            return ret.text
        except requests.HTTPError as e:
            time.sleep(timeout)
            continue

def main():
    setup_db()
    # Create NewsSource entries if they don't already exist
    with sqlite3.connect("News.db") as conn:
        cursor = conn.cursor()

        for source in NEWS_SOURCES:
            rss_feed = fetch_with_retry(source["url"])

            cursor.execute(""" 
                INSERT INTO NewsSources (name, url, last_queried, rss_content, hash)
                VALUES (?, ?, ?, ?, ?)
                """, (source["name"], source["url"], int(time.time()), rss_feed, "NOT HASHED"))
        conn.commit()
    tagesschau = NewsSite(1)
    welt = NewsSite(2)
    sz = NewsSite(3)
    spiegel = NewsSite(4)

if __name__ == "__main__":
    main()