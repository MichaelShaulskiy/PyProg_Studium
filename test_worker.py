''' NUR UM ZU TESTEN OB MEIN SLOT IM MAINWINDOW-PROGRAMM AUCH LÄUFT'''

import sqlite3
from PySide6.QtCore import QObject, Signal, QThread

class BackendWorker(QThread):
    results_ready = Signal(list)
    processing_complete = Signal()

    def __init__(self, settings):
            super().__init__()
            self.settings = settings
            
    def run(self):
            try:
                # Datenbankabfrage basierend auf settings
                results = []
                with sqlite3.connect("News.db") as conn:
                    cursor = conn.cursor()
                    
                    if self.settings.get("spiegel", True):
                        cursor.execute("SELECT summary FROM NewsArticles WHERE source_id = 1")
                        results.extend(cursor.fetchall())
                        
                
                self.results_ready.emit(results)
                
            except Exception as e:
                print(f"Fehler bei der Backend-Verarbeitung: {e}")
            finally:
                self.processing_complete.emit()

class NewsBackend(QObject):
    # Signale für die Kommunikation mit der UI
    results_available = Signal(list)
    processing_finished = Signal()
    
    def __init__(self):
        super().__init__()
        self.worker = None
    
    def process_settings(self, settings):
        """Startet die Backend-Verarbeitung mit den übergebenen Einstellungen"""
        # Worker erstellen und Signale verbinden
        self.worker = BackendWorker(settings)
        self.worker.results_ready.connect(self.results_available)
        self.worker.processing_complete.connect(self.processing_finished)
        
        # Thread starten
        self.worker.start()