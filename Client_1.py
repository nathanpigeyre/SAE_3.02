import socket
import threading
import sys
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *


def receive_messages(client_socket, usernamelog, usernamesign):
    while True:
        try:
            reply = client_socket.recv(1024).decode()
            if reply == 'Kill':
                print("Le serveur est kill")
                client_socket.close()
                break

            if reply.startswith("!") and (reply[1:] == usernamelog or reply[1:] == usernamesign):
                print("Vous avez été BAN !!!")
                client_socket.close()
                break

            if reply.startswith("~"):
                kick = reply[1:].split(":")
                if len(kick) == 2 and (kick[0] == usernamelog or kick[0] == usernamesign):
                    print("Vous avez été Kick pendant {} minute(s) !!!".format(kick[1]))
                    client_socket.close()
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

def user_choice():
    while True:
        try:
            log_sign = int(input("1 to sign, 2 to log : "))
            if log_sign == 1 or log_sign == 2:
                return log_sign
            else:
                print("Veuillez entrer 1 ou 2.")
        except ValueError:
            print("Veuillez entrer un nombre.")
def main():
    ip_address = "127.0.0.1"
    port = 1506
    usernamelog = ""
    usernamesign = ""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip_address, port))
    try:
        log_sign = user_choice()
        if log_sign == 1:
            sign = "sign"
            client_socket.send(sign.encode())
            usernamesign = input("Ton Nom: ")
            passwordsign = input("Ton Mot de Passe: ")
            client_socket.send(usernamesign.encode())
            client_socket.send(passwordsign.encode())

        elif log_sign == 2:
            log = "log"
            client_socket.send(log.encode())
            usernamelog = input("Ton Nom: ")
            passwordslog = input("Ton Mot de Passe: ")
            client_socket.send(usernamelog.encode())
            client_socket.send(passwordslog.encode())

        registration_status = client_socket.recv(1024).decode()
        print(registration_status)
        if "réussie" in registration_status:
            receive_thread = threading.Thread(target=receive_messages, args=(client_socket,usernamelog,usernamesign))
            receive_thread.start()
            Connected = True
            while Connected == True:
                To = input("Who: ")
                You = input("You: ")
                message_send = To +'/' + You
                try:
                    client_socket.send(message_send.encode())
                except ConnectionAbortedError:
                    print("Le serveur n'est pas connecté")
                    Connected = False
                except ConnectionResetError:
                    Connected = False
                except OSError:
                    Connected = False


    except ValueError:
        print("Valeur inconnue")
        client_socket.close()
    except OSError:
        print("Erreur de connexion")
        client_socket.close()
    except UnboundLocalError:
        print("Valeur inconnue")
        client_socket.close()

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


if __name__ == "__main__":
    main()



