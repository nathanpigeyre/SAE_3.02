import sys
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from Client_1 import main



class LOGIN(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Discord-style App")
        self.setGeometry(900, 400, 130, 200)

        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)
        self.layout = QVBoxLayout(self.widget)

        self.stacked_widget = QStackedWidget(self)
        self.layout.addWidget(self.stacked_widget)

        login_widget = QWidget(self)
        self.login_layout = QVBoxLayout(login_widget)
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.on_login_clicked)
        sign_up_button = QPushButton("Sign Up")
        sign_up_button.clicked.connect(self.on_sign_up_clicked)
        self.login_layout.addWidget(QLabel("Username:"))
        self.login_layout.addWidget(self.username_input)
        self.login_layout.addWidget(QLabel("Password:"))
        self.login_layout.addWidget(self.password_input)
        self.login_layout.addWidget(login_button)
        self.login_layout.addWidget(sign_up_button)
        self.stacked_widget.addWidget(login_widget)


        self.stacked_widget.setCurrentIndex(0)

    def on_login_clicked(self):
        # Logique pour vérifier l'authentification ici
        # Si l'authentification est réussie :

        print('log')

    def on_sign_up_clicked(self):
        # Logique pour gérer l'inscription ici
        # Si l'inscription est réussie :

        print('sing')
class Discord(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Discord-style App")
        self.setGeometry(100, 100, 800, 600)

        
        widget = QWidget(self)
        self.setCentralWidget(widget)

       
        layout = QVBoxLayout(widget)

        
        sidebar = QToolBar("Sidebar")
        sidebar.setOrientation(Qt.Orientation.Vertical)
        sidebar.setIconSize(QSize(32, 32))
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, sidebar)


        
        disconnect_button = QPushButton("Déconnecter")
        button1 = QPushButton("Message Privé")
        button2 = QPushButton("Géneral")
        button3 = QPushButton("Blabla")
        button4 = QPushButton("Comptabilité")
        button5 = QPushButton("Informatique")
        button6 = QPushButton("Marketing")
        
        
    
        disconnect_button.clicked.connect(self.on_disconnect_clicked)
        sidebar.addWidget(disconnect_button)
        spacer = QLabel()
        spacer.setFixedHeight(30)
        sidebar.addWidget(spacer)

        sidebar.addWidget(button1)
        spacer = QLabel()
        spacer.setFixedHeight(10)
        sidebar.addWidget(spacer)

        sidebar.addWidget(button2)
        spacer = QLabel()
        spacer.setFixedHeight(10)
        sidebar.addWidget(spacer)

        sidebar.addWidget(button3)
        spacer = QLabel()
        spacer.setFixedHeight(10)
        sidebar.addWidget(spacer)

        sidebar.addWidget(button4)
        spacer = QLabel()
        spacer.setFixedHeight(10)
        sidebar.addWidget(spacer)

        sidebar.addWidget(button5)
        spacer = QLabel()
        spacer.setFixedHeight(10)
        sidebar.addWidget(spacer)

        sidebar.addWidget(button6)

        
        self.chat = QVBoxLayout()
        self.chat_area = QWidget(self)
        self.chat_area.setLayout(self.chat)
        layout.addWidget(self.chat_area)

        
        self.message_input = QLineEdit(self)
        layout.addWidget(self.message_input)

       
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.on_send_clicked)
        layout.addWidget(send_button)

        
        sidebar_width = self.width() // 6
        sidebar.setFixedWidth(sidebar_width)

        
        button1.clicked.connect(self.on_button1_clicked)
        button2.clicked.connect(self.on_button2_clicked)
        button2.clicked.connect(self.on_button3_clicked)
        button2.clicked.connect(self.on_button4_clicked)
        button2.clicked.connect(self.on_button5_clicked)
        button2.clicked.connect(self.on_button6_clicked)


    def on_button1_clicked(self):
        self.clear_chat_area()

        # Create and add dynamic buttons to the chat area layout
        for i in range(1, 6):
            dynamic_button = QPushButton(f"Dynamic Button {i}")
            dynamic_button.clicked.connect(self.on_dynamic_button_clicked)
            self.chat.addWidget(dynamic_button)


    def on_button2_clicked(self):
        self.clear_chat_area()
    def on_button3_clicked(self):
        self.clear_chat_area()
    def on_button4_clicked(self):
        self.clear_chat_area()
    def on_button5_clicked(self):
        self.clear_chat_area()
    def on_button6_clicked(self):
        self.clear_chat_area()
        

    def on_dynamic_button_clicked(self):
        self.clear_chat_area()
        

    def on_disconnect_clicked(self):
        print("Déconnecté")
        

    def on_send_clicked(self):
        message_text = self.message_input.text()
        self.message_input.clear()
        self.add_text_to_chat_area(f"You: {message_text}")

    def clear_chat_area(self):
        # Clear existing content in the chat area layout
        while self.chat.count():
            child = self.chat.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def add_text_to_chat_area(self, text):
        label = QTextEdit(self)
        label.setPlainText(text)
        label.setReadOnly(True)
        self.chat.addWidget(label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LOGIN()
    window.show()
    sys.exit(app.exec())
