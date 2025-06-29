import os
from PySide6.QtCore import QSize, Qt, QDate, QThread, Signal, Slot
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QToolBar, QTextEdit, QMessageBox, QVBoxLayout, QWidget

class SummaryWindow(QWidget):

    def __init__(self, results = None):
        super().__init__()
        self.results = results
        self.setup_summary_window()

    def setup_summary_window(self):
        self.setWindowTitle("Zusammenfassungen")
        self.setup_notepad()
        self.setup_toolbar()
        self.setup_layout()

    def setup_toolbar(self):
        self.toolbar = QToolBar()
        self.cut_function = QAction("Cut", self)
        self.toolbar.addAction(self.cut_function)
        self.cut_function.triggered.connect(self.notepad.cut)

        self.copy_function = QAction("Copy", self)
        self.toolbar.addAction(self.copy_function)
        self.copy_function.triggered.connect(self.notepad.copy)

        self.paste_function = QAction("Paste", self)
        self.toolbar.addAction(self.paste_function)
        self.paste_function.triggered.connect(self.notepad.paste)

        self.undo_function = QAction("Undo", self)
        self.toolbar.addAction(self.undo_function)
        self.undo_function.triggered.connect(self.notepad.undo)

        self.redo_function = QAction("Redo", self)
        self.toolbar.addAction(self.redo_function)
        self.redo_function.triggered.connect(self.notepad.redo)

        self.toolbar.addSeparator()

        self.save_function = QAction("Save", self)
        self.toolbar.addAction(self.save_function)
        self.save_function.triggered.connect(self.save_to_txt) 

        self.close_function = QAction("Close", self)
        self.toolbar.addAction(self.close_function)
        self.close_function.triggered.connect(self.close)
    
    def save_to_txt (self):
        with open("News_Summary.txt", "w") as file:
            file.write(self.notepad.toPlainText())

        confirmation_msg = QMessageBox()
        confirmation_msg.setText(str("Zusammenfassung wurde unter dem aktuellen Pfad als News_Summary.txt gespeichert"))
        confirmation_msg.exec()

    def setup_notepad(self):
        # QTextEdit kann (nativ) keine klickbaren Links darstellen. Das würde mit QTextBrowser gehen - dann verlieren wir aber die Bearbeitungsfunktionalität... 
        self.notepad = QTextEdit()
        self.notepad.setHtml(self.show_articles())
        #self.notepad.setOpenExternalLinks(True) #funktioniert nur bei QTextBrowser

    def setup_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.notepad)
        self.setLayout(layout)

    def show_articles(self):
        try:
             if not self.results: 
                return "<p>Keine Artikel gefunden.</p>"
             
             formatted_text = "<h2>Artikel aus der Datenbank</h2>"
             for result in self.results:
                    article_text = result[0]
                    formatted_text += f"<p>{article_text}</p><hr>"
             return formatted_text
        except Exception as e: 
            return f"<p>Fehler beim Laden der Artikel: {str(e)}</p>"
