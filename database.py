from PySide6.QtCore import QObject, Signal, Slot, QCoreApplication
from pathlib import Path
import sqlite3

_global_db = None

def get_db_connection():
    global _global_db

    if _global_db is None:
        _global_db = sqlite3.connect("News.db")

    return _global_db

def close_db():
    global _global_db

    if _global_db is not None:
        _global_db.close()
        _global_db = None
