from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import socket
import threading


class LOGIN(QWidget):
    open_discord_signal = pyqtSignal()
    close_login_window_signal = pyqtSignal()
    def __init__(self, client_socket):
        super().__init__()

        self.client_socket = client_socket


        self.setWindowTitle("Discord-style App")
        self.setGeometry(900, 400, 400, 300)

        self.layout = QVBoxLayout(self)

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

        # Ajout de la zone de texte pour afficher les messages
        self.message_display = QTextEdit(self)
        self.layout.addWidget(self.message_display)

        # Variables pour stocker les noms d'utilisateur
        self.usernamelog = ""
        self.usernamesign = ""

        # Lancement du thread pour recevoir les messages
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

        # Connexion du signal personnalisé au slot pour ouvrir la fenêtre Discord
        self.open_discord_signal.connect(self.open_discord)
        self.close_login_window_signal.connect(self.close)

    def on_login_clicked(self):
        log = "log"
        self.client_socket.send(log.encode())
        self.usernamelog = self.username_input.text()
        passwordslog = self.password_input.text()
        self.client_socket.send(self.usernamelog.encode())
        self.client_socket.send(passwordslog.encode())

    def on_sign_up_clicked(self):
        sign = "sign"
        self.client_socket.send(sign.encode())
        self.usernamesign = self.username_input.text()
        passwordsign = self.password_input.text()
        self.client_socket.send(self.usernamesign.encode())
        self.client_socket.send(passwordsign.encode())

    def receive_messages(self):
        while True:
            try:
                reply = self.client_socket.recv(1024).decode()

                if "réussie" in reply:
                    self.open_discord_signal.emit()
                    self.close_login_window_signal.emit()



                if reply == 'Kill':
                    print("Le serveur est kill")
                    self.close_app_signal.emit()
                    self.client_socket.close()
                    break

                if reply.startswith("!") and (reply[1:] == self.usernamelog or reply[1:] == self.usernamesign):
                    print("Vous avez été BAN !!!")
                    self.close_app_signal.emit()
                    self.client_socket.close()
                    break

                if reply.startswith("~"):
                    kick = reply[1:].split(":")
                    if len(kick) == 2 and (kick[0] == self.usernamelog or kick[0] == self.usernamesign):
                        print("Vous avez été Kick pendant {} minute(s) !!!".format(kick[1]))
                        self.close_app_signal.emit()
                        self.client_socket.close()
                        break

                if not reply:
                    print("Connexion perdue avec le serveur")
                    break
                print(reply)
            except ConnectionResetError:
                print("Connexion perdue avec le serveur")
                break
            except OSError:
                print("Connexion perdue avec le serveur")

    def open_discord(self):
        self.discord_window = Discord()
        self.discord_window.show()

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
def main():
    ip_address = "127.0.0.1"
    port = 1506
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip_address, port))

    app = QApplication([])
    login_window = LOGIN(client_socket)
    login_window.show()
    app.exec()

if __name__ == "__main__":
    main()