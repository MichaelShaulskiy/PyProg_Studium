''' NUR UM ZU TESTEN OB MEIN SLOT IM MAINWINDOW-PROGRAMM AUCH LÄUFT'''
import time
import sqlite3
from PySide6.QtCore import QObject, Signal
from main import QNewsBackend

class NewsBackend(QObject):
    results_available = Signal(list)
    processing_finished = Signal()

    def __init__(self):
        super().__init__()
        self.worker = None

    def process_settings(self, settings):
        # Create and start the worker thread
        self.worker = QNewsBackend(settings)
        self.worker.results_ready.connect(self.results_available)
        self.worker.processing_complete.connect(self.processing_finished)
        self.worker.start()