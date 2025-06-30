from database import get_db_connection
from bs4 import BeautifulSoup
import requests as req
from pprint import pprint
import sqlite3

class RSSChannelMetadata:

    class DublinCore:

        def __init__(self) -> None:
            self.publisher = None
            self.rights = None
            self.date = None
            self.source = None

    def __init__(self) -> None:
        self.title = None
        self.link = None
        self.description = None
        self.language = None
        self.copyright = None
        self.lastBuildDate = None
        self.pubDate = None
        self.docs = None
        self.ttl = None
        self.dc = self.DublinCore()
        self.dc.publisher = None
        self.dc.rights = None
        self.dc.date = None
        self.dc.source = None

class RSSItem:

    def __init__(self, title: str, link: str, description = None, pubDate = None, guid = None) -> None:
        self.title = title
        self.link = link
        self.description = description
        self.pubDate = pubDate
        self.guid = guid

class RSS(object):

    def __init__(self, source_index: int) -> None:
        conn = sqlite3.connect("News.db")
        #self.feed_url = url
        self.source_index = source_index
        self.feed_content = None
        self.metadata = RSSChannelMetadata()

        cursor = conn.cursor()
        result = cursor.execute("SELECT rss_content FROM NewsSources WHERE source_id = ?", (self.source_index,))

        result = result.fetchone()

        if result:
            self.feed_content = result[0]


        self.soup = BeautifulSoup(self.feed_content, "xml")
        self.root_node = self.soup.rss

    def items(self):
        """
        Generator constructing RSSItem Instances
        """
        item_tags = self.root_node.channel.find_all("item")
        ret = []

        for tag in item_tags:
            curr = RSSItem(tag.title.string, tag.link.string)
            if tag.description:
                curr.description = tag.description
            if tag.pubDate:
                curr.pubDate = tag.pubDate
            if tag.guid:
                curr.guid = tag.guid
            ret.append(curr)
        return ret
    
if __name__ == "__main__":
    ts = RSS("haslkfhsd")
    #pprint(ts.soup)
    soup = ts.soup
    #pprint(soup.namespace)
    #pprint(soup.is_xml)
    #for item in ts.root_node.channel.children:
    #    print(item.name)
    for item in ts.items():
        pprint(item)
        pprint(item.title)