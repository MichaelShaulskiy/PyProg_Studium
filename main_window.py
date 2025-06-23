import os
from PySide6.QtCore import QSize, Qt, QDate
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter
from PySide6.QtWidgets import (QMainWindow, QPushButton, QStatusBar, QToolBar, QTextEdit, QMessageBox,
QHBoxLayout, QVBoxLayout, QWidget, QLabel, QSlider, QDateEdit, QSizePolicy, QCalendarWidget
)

class MainWindow(QMainWindow):

    # setup the main window, the relative image path, the GUI widgets and the main-window-layout
    def __init__(self, app): 
        super().__init__()
        self.app = app
        self.base_path = os.path.dirname(os.path.abspath(__file__)) 
        self.image_path = os.path.join(self.base_path, "Images")
        self.setup_window()
        self.create_widgets()
        self.setup_main_layout()
         
    # setup the frame of the main window
    def setup_window(self):
        self.setWindowTitle("NewsProvider")
        self.setFixedSize(800, 600)  
        self.setStatusBar(QStatusBar(self))

    # call functions for every widget used in the main window
    def create_widgets(self):
        self.create_provider_buttons()
        self.create_labels()
        self.create_date_edit()
        self.create_go_button()
        self.create_slider()
        self.create_design_element()

    # setup the 4 provider buttons to check which news-provider you would like to get infos from.
    # add matching icons, call the button-style-function and connect the buttons to each clicked-function
    def create_provider_buttons(self):
        '''PROVIDER BUTTONS'''
        #tbd: Icons github 
        self.spiegel_button = QPushButton(icon=QIcon(os.path.join(self.image_path, "Spiegel.jpg")))
        self.apply_provider_button_style(self.spiegel_button)
        self.spiegel_button.clicked.connect(self.spiegel_clicked)

        self.tagesschau_button = QPushButton(icon=QIcon(os.path.join(self.image_path, "Tagesschau.jpg")))
        self.apply_provider_button_style(self.tagesschau_button)
        self.tagesschau_button.clicked.connect(self.tagesschau_clicked)

        self.welt_button = QPushButton(icon=QIcon(os.path.join(self.image_path, "Welt.png")))
        self.apply_provider_button_style(self.welt_button)
        self.welt_button.clicked.connect(self.welt_clicked)

        self.sz_button = QPushButton(icon=QIcon(os.path.join(self.image_path, "SZ.png")))
        self.apply_provider_button_style(self.sz_button)
        self.sz_button.clicked.connect(self.sz_clicked)

    # setup every (informative/header) label & show some info at the statusbar when hovering over each label
    def create_labels(self):
        '''LABELS'''
        self.provider_label = QLabel("Set Providers ⓘ")
        self.provider_label.enterEvent = lambda z: self.statusBar().showMessage("Nachrichtenquellen ein-  oder ausschließen. Default: Alle eingeschlossen")
        self.provider_label.leaveEvent = lambda z: self.statusBar().clearMessage()

        self.date_label = QLabel("Set Date ⓘ")
        self.date_label.enterEvent = lambda z: self.statusBar().showMessage("Tag der gewünschten Zusammenfassung wählen.")
        self.date_label.leaveEvent = lambda z: self.statusBar().clearMessage()

        self.slider_label = QLabel("Set Length ⓘ")
        self.slider_label.enterEvent = lambda z: self.statusBar().showMessage("Länge der gewünschten Zusammenfassung wählen. Default sind 2 Sätze pro Artikel")
        self.slider_label.leaveEvent = lambda z: self.statusBar().clearMessage()

    # setup the calendar/date-edit with a calendar popup to get the news of the selected date (if possible).
    # Default is today
    def create_date_edit(self):
        '''DATE-EDIT'''
        
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        today = QDate.currentDate()
        self.date_edit.setDate(today)
        self.date_edit.setCalendarPopup(True)



    # setup the GO! Button, apply it's own style and connect the clicked-function
    def create_go_button(self):
        '''GO BUTTON'''
        #tbd: connection -> new window 
        self.go_button = QPushButton("GO!")
        self.apply_go_button_style(self.go_button)
        self.go_button.clicked.connect(self.go_button_clicked)
    
    # setup slider to set the desired summary length 
    def create_slider(self):
        '''SLIDER'''
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.apply_slider_style(self.slider)
        self.slider.valueChanged.connect(self.summary_length_changed)

    # setup the left-bound design element (just for aesthetic purposes)
    # opens the image into a label with a fixed width of 1/3 of the main window. Crops to set the desired width if necessary
    def create_design_element(self):
        '''DESIGN-ELEMENT'''
        design_path = os.path.join(self.image_path, "Design.jpeg")
        try:
            with open(design_path):
                self.design_label = QLabel()
                pixmap = QPixmap(design_path)
                
                image_width = self.width() // 3
                self.design_label.setFixedWidth(image_width)
                
                scaled_pixmap = pixmap.scaledToWidth(
                image_width, 
                Qt.TransformationMode.SmoothTransformation #smooth zooming/interpolation 
                )

                self.design_label.setPixmap(scaled_pixmap)
            
            self.design_label.setAlignment(Qt.AlignCenter)

        except:
            self.design_label = QLabel("Bild nicht gefunden")

    # setup the main layout with nested layout-functions. 
    # main-layout consists of the design-element on the left and the widgets on the right. 
    def setup_main_layout(self):
        container = QWidget()
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.design_label)

        v_layout_right = self.create_right_v_layout()
        h_layout.addLayout(v_layout_right)
        
        container.setLayout(h_layout)
        self.setCentralWidget(container)

    # setup the nested layout with the widgets on the right starting from the top.
    def create_right_v_layout(self):
        v_layout = QVBoxLayout()

        # the 4 provider buttons are nested in the create buttons layout function.
        '''Provider Area'''
        v_layout.addWidget(self.provider_label)
        v_layout.addLayout(self.create_provider_buttons_layout())
        
        '''Date-Edit Area'''
        v_layout.addWidget(self.date_label)
        v_layout.addWidget(self.date_edit)
    
        '''Slider Area'''
        v_layout.addWidget(self.slider_label)
        v_layout.addWidget(self.slider)

        # the GO!-button is placed on the lower right corner
        '''GO! Button Area'''
        go_layout = QHBoxLayout()
        go_layout.addStretch(1)  
        go_layout.addWidget(self.go_button)
        v_layout.addLayout(go_layout)

        return v_layout # to use the v_layout in the main_layout function

    # setup the last nested layout function for the provider buttons.
    def create_provider_buttons_layout(self):
        v_layout = QVBoxLayout()
        
        '''Upper Row'''
        h_layout_1 = QHBoxLayout()
        h_layout_1.addWidget(self.spiegel_button)
        h_layout_1.addWidget(self.tagesschau_button)
        v_layout.addLayout(h_layout_1)

        '''Lower Row'''
        h_layout_2 = QHBoxLayout()
        h_layout_2.addWidget(self.welt_button)
        h_layout_2.addWidget(self.sz_button)
        v_layout.addLayout(h_layout_2)

        return v_layout # to use the v_layout in the "create_right_v_layout" function

    # setup the stylesheet of the provider buttons 
    # Set them as checkable, default is checked, with some more design ideas to make them look good and "clickable"
    def apply_provider_button_style(self, button):
        button.setCheckable(True)
        button.setChecked(True)
        button.setFixedSize(120,120)
        button.setIconSize(QSize(115, 115))
        button.setStyleSheet("""
            QPushButton {
                padding: 0px;
                border: 2px solid #cccccc;
                border-radius: 5px;
            }
            QPushButton:hover {
                border: 2px solid #3daee9;
                background-color: rgba(61, 174, 233, 20);
            }
            QPushButton:pressed {
                border: 3px solid #2980b9;
                background-color: rgba(61, 174, 233, 50);
            }
            QPushButton:checked {
                border: 3px solid #27ae60;
                background-color: rgba(39, 174, 96, 30);
            }
        """)

    # setup the stylesheet for the different looking "GO!" button
    # also make it look good and "clickable"
    def apply_go_button_style(self, button):
       button.setStyleSheet("""
            QPushButton {
                background-color: #00AB66;
            }
            QPushButton:hover {
                border: 2px solid #3daee9;
                background-color: #00AB66;
            }
            QPushButton:pressed {
                border: 3px solid #2980b9;
                background-color: #009257;
            }
            QPushButton:checked {
                border: 3px solid #27ae60;
                background-color: #009257;
            }
        """)

    # button connections to the backend
    def spiegel_clicked(self):
        self.statusBar().showMessage("Spiegel clicked", 2000)
     
    # button connections to the backend
    def welt_clicked(self):
        self.statusBar().showMessage("Welt clicked", 2000)

    # button connections to the backend
    def tagesschau_clicked(self):
        self.statusBar().showMessage("Tagesschau clicked", 2000)

    # button connections to the backend
    def sz_clicked(self):
        self.statusBar().showMessage("Süddeutsche clicked", 2000)

    # setup the slider style to make it more intuitive to use
    def apply_slider_style(self, slider):
        slider.setMinimum(1)
        slider.setMaximum(4)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(1)

    # show an infomsg at the statusbar if the user changes the desired length of the summary
    def summary_length_changed(self, value):
         if value == 1:
              self.statusBar().showMessage("Kurze Zusammenfassung (1 Satz)",2000)
         elif value == 2:
              self.statusBar().showMessage("Mittlere Zusammenfassung (2 Sätze)",2000)
         elif value == 3:
              self.statusBar().showMessage("Längere Zusammenfassung (4 Sätze)",2000)
         elif value == 4:
              self.statusBar().showMessage("Ausführliche Zusammenfassung (6 Sätze)",2000)

    # connect go button 
    def go_button_clicked(self):
         self.statusBar().showMessage("Go! clicked", 2000)
         self.summary_window = SummaryWindow()
         self.summary_window.show()

class SummaryWindow(QWidget):

    def __init__(self):
        super().__init__()
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
        self.notepad.setHtml(self.html_test())
        self.notepad.setOpenExternalLinks(True)

    def setup_layout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.notepad)
        self.setLayout(layout)

    def html_test(self):
        self.text ="""<ol>
	<li>Aber Kay, der kleine Kay! fragte Gerda. Wann kam er? Befand er sich unter der Menge?</li>
	<li>Eil mit Weile! nun sind wir gerade bei ihm! Am dritten Tage kam eine kleine Person, weder mit Pferd, noch mit Wagen, ganz lustig und guter Dinge gerade auf das Schloss hinaufspaziert. Seine Augen blitzten wie deine, er hatte prächtiges langes Haar, aber sonst ärmliche Kleider.</li>
	<li>Da war Kay! jubelte Gerda. O, dann habe ich ihn gefunden und dabei klatschte sie in die Hände.
</li>
	<li>Er hatte einen kleinen Ranzen auf seinem Rücken! sagte die Krähe.</li>
    https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=RDdQw4w9WgXcQ&start_radio=1&ab_channel=RickAstley
	<li>Nein, das war sicherlich sein Schlitten! sagte Gerda, denn damit ging er fort!</li>
</ol>"""
        return self.text
    