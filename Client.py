from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import socket
import threading
import re
class LOGIN(QWidget):
    """
        Il y a 3 classes dans mon client, la première est le LOGIN (la page d'inscription)
        celle-ci permet de récupérer les identifiant et de les envoyer au serveur pour qu'il
        check s'ils existent.
    """
    open_choix_signal = pyqtSignal()
    close_login_window_signal = pyqtSignal()
    open_discord_signal = pyqtSignal()



    def __init__(self, client_socket):
        """
            Cette partie est la partie graphique.
        """
        super().__init__()

        self.close_login_window_signal.connect(self.close_login_window)
        self.client_socket = client_socket

        self.setWindowTitle("Discord App")
        self.setGeometry(900, 400, 400, 300)

        self.layout = QVBoxLayout(self)

        self.stacked_widget = QStackedWidget(self)
        self.layout.addWidget(self.stacked_widget)

        login_widget = QWidget(self)
        self.login_layout = QVBoxLayout(login_widget)
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.on_login_clicked)
        self.sign_up_button = QPushButton("Sign Up")
        self.sign_up_button.clicked.connect(self.on_sign_up_clicked)
        self.login_layout.addWidget(QLabel("Username:"))
        self.login_layout.addWidget(self.username_input)
        self.login_layout.addWidget(QLabel("Password:"))
        self.login_layout.addWidget(self.password_input)
        self.login_layout.addWidget(self.login_button)
        self.login_layout.addWidget(self.sign_up_button)
        self.stacked_widget.addWidget(login_widget)

        self.stacked_widget.setCurrentIndex(0)

        self.usernamelog = ""
        self.usernamesign = ""

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()


    """
        Cette partie consiste à envoyer !#log ou !#sign au serveur puis après envoyer les username et password.
    """
    def on_login_clicked(self):
        log = "!#log"
        self.client_socket.send(log.encode())
        self.usernamelog = self.username_input.text()
        passwordslog = self.password_input.text()
        self.client_socket.send(self.usernamelog.encode())
        self.client_socket.send(passwordslog.encode())

        self.open_discord_signal.connect(self.open_discord)
        self.close_login_window_signal.connect(self.close)
        self.open_discord_signal.emit()
    def on_sign_up_clicked(self):
        sign = "!#sign"
        self.client_socket.send(sign.encode())
        self.usernamesign = self.username_input.text()
        passwordsign = self.password_input.text()
        self.client_socket.send(self.usernamesign.encode())
        self.client_socket.send(passwordsign.encode())
        self.open_choix_signal.connect(self.open_choix)
        self.close_login_window_signal.connect(self.close)



    def receive_messages(self):
        """
            Cette partie est la réception de tout les massages, des kicks, des bans, des kills,
            des messages que l'on reçoit pour faire des box d'alertes.
            On reçoit aussi ici le fait de mettre visible ou non les salons ou l'utilisateur a accès.
        """
        while True:
            try:
                reply = self.client_socket.recv(1024).decode()

                if "réussie" in reply:
                    self.close_login_window_signal.emit()
                    self.open_choix_signal.emit()


                if not reply:
                    QMessageBox.warning("Message Serveur", "Connexion perdue avec le serveur.")
                    break

                if reply == 'Kill':
                    self.client_socket.close()
                    QMessageBox.warning("Message Serveur", "Le Serveur est Kill.")
                    break

                if reply.startswith("!") and (reply[1:] == self.usernamelog or reply[1:] == self.usernamesign):
                    self.client_socket.close()
                    QMessageBox.warning(self, "Message Serveur", "Vous avez été Ban.")
                    break

                if reply.startswith("~"):
                    kick = reply[1:].split(":")
                    if len(kick) == 2 and (kick[0] == self.usernamelog or kick[0] == self.usernamesign):
                        QMessageBox.warning(self, "Message Serveur", "Vous avez été Kick pour {} minute(s).".format(kick[1]))
                        self.client_socket.close()
                        break

                if reply.startswith("Identifiants"):
                    QMessageBox.warning(self, "Erreur de connexion","Identifiants incorrects. Veuillez recommencer.")

                if reply.startswith("Warning!"):
                    QMessageBox.warning(self, "Erreur d'identification","Identifiants déjà existant. Veuillez recommencer.")

                if reply.startswith("No password"):
                    QMessageBox.warning(self, "Erreur d'identification","Vous n'avez pas rentré de password et/ou d'identifiant.")

                if reply.startswith("Reconnexion"):
                    nombre = re.search(r'\d+', reply)
                    if nombre:
                        lenombre = int(nombre.group())
                        QMessageBox.warning(None, "Message Serveur",f"L'identifiant est actuellement Kick pendant {lenombre} minute(s).")
                if reply.startswith("%") and (reply[1:] == self.usernamelog or reply[1:] == self.usernamesign):
                    print('ca marche')
                    droit = reply.split('/')
                    droits = droit[1].split(',')
                    button3 = False
                    button4 = False
                    button5 = False
                    button6 = False
                    print(droits)
                    for mot in droits:
                        if "Blabla" == mot:
                            button3 = True
                        elif "Comptabilite" == mot:
                            button4 = True
                        elif "Informatique" == mot:
                            button5 = True
                        elif "Marketing" == mot:
                            button6 = True
                    self.check_condition(button3, button4, button5, button6)



                print('\n' + reply)

            except ConnectionResetError:
                QMessageBox.warning(self, "Message Serveur", "Connexion réinitialisée par le serveur.")
                break
            except OSError as e:
                QMessageBox.warning(self, "Erreur OS", f"Erreur OS lors de la réception : {e}")
                break
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Une erreur s'est produite : {e}")
                break

    """
        On a aussi ici les def pour la bien séance de tout donc l'ouverture et les fermetures des autres pages.
    """

    def close_login_window(self):
        self.close()
    def open_choix(self):
        self.choix_window = SalonSelection(self.client_socket)
        self.choix_window.show()
    def open_discord(self):
        self.discord_window = Discord(self.client_socket)
        self.close_login_window_signal.emit()
        self.discord_window.show()



class SalonSelection(QWidget):
    """
        Voici ici la deuxième classe qui permet de choisir les salons auquel vous voulez avoir accès.
    """
    open_discord_signal = pyqtSignal()
    close_choix_window_signal = pyqtSignal()
    def __init__(self, client_socket):
        """
            Voici la partie graphique.
        """
        super().__init__()
        self.close_choix_window_signal.connect(self.close_choix_window)
        self.client_socket = client_socket
        self.setWindowTitle("Sélection des Salons")
        self.setGeometry(900, 400, 400, 300)

        self.layout = QVBoxLayout()

        self.checkbox_blabla = QCheckBox("Blabla")
        self.checkbox_comptabilite = QCheckBox("Comptabilité")
        self.checkbox_informatique = QCheckBox("Informatique")
        self.checkbox_marketing = QCheckBox("Marketing")

        self.layout.addWidget(self.checkbox_blabla)
        self.layout.addWidget(self.checkbox_comptabilite)
        self.layout.addWidget(self.checkbox_informatique)
        self.layout.addWidget(self.checkbox_marketing)

        self.button_valider = QPushButton("Valider")
        self.button_valider.clicked.connect(self.valider_selection)
        self.layout.addWidget(self.button_valider)

        self.setLayout(self.layout)

        self.open_discord_signal.connect(self.open_discord)
        self.close_choix_window_signal.connect(self.close)



    def valider_selection(self):
        """
            Cette partie nous sert à confirmer et à mettre dans une liste les choix de salon du users.
            Ainsi que l'envoyer au serveur avec le %!§ devant pour que le serveur puisse comprendre directement,
            que c'est de l'envoi de chanels.
        """
        selections = []
        if self.checkbox_blabla.isChecked():
            selections.append("Blabla")
        if self.checkbox_comptabilite.isChecked():
            selections.append("Comptabilite")
        if self.checkbox_informatique.isChecked():
            selections.append("Informatique")
        if self.checkbox_marketing.isChecked():
            selections.append("Marketing")


        message = ','.join(selections)
        messages = '%!§' + message
        self.client_socket.send(messages.encode())
        self.client_socket.send(messages.encode())
        self.open_discord_signal.emit()

    """
         On a aussi ici les def pour la bien séance de tout donc l'ouverture et les fermetures des autres pages.
    """

    def close_choix_window(self):
        self.close()

    def open_discord(self):
        self.discord_window = Discord(self.client_socket)
        self.close_choix_window_signal.emit()
        self.discord_window.show()



class Discord(QMainWindow):
    """
        Enfin voici notre 3e classe qui est le gros de l'application la page principal.
    """
    def __init__(self, client_socket):
        """
            Voici la partie graphique.
        """
        super().__init__()
        self.client_socket = client_socket

        self.setWindowTitle("Discord-style App")
        self.setGeometry(450, 200, 800, 600)

        widget = QWidget(self)
        self.setCentralWidget(widget)

        layout = QVBoxLayout(widget)

        self.chat = QVBoxLayout()
        self.chat_area = QWidget(self)
        self.chat_area.setLayout(self.chat)
        layout.addWidget(self.chat_area)

        sidebar = QToolBar("Sidebar")
        sidebar.setOrientation(Qt.Orientation.Vertical)
        sidebar.setIconSize(QSize(32, 32))
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, sidebar)

        disconnect_button = QPushButton("Déconnecter")
        self.button1 = QPushButton("Message Privé")
        self.button2 = QPushButton("Géneral")
        self.button3 = QPushButton("Blabla")
        self.button4 = QPushButton("Comptabilité")
        self.button5 = QPushButton("Informatique")
        self.button6 = QPushButton("Marketing")
        self.button3.setVisible(True)
        self.button4.setVisible(True)
        self.button5.setVisible(True)
        self.button6.setVisible(True)



        disconnect_button.clicked.connect(self.on_disconnect_clicked)
        sidebar.addWidget(disconnect_button)
        spacer = QLabel()
        spacer.setFixedHeight(30)
        sidebar.addWidget(spacer)

        sidebar.addWidget(self.button1)
        spacer = QLabel()
        spacer.setFixedHeight(10)
        sidebar.addWidget(spacer)

        sidebar.addWidget(self.button2)
        spacer = QLabel()
        spacer.setFixedHeight(10)
        sidebar.addWidget(spacer)

        sidebar.addWidget(self.button3)
        spacer = QLabel()
        spacer.setFixedHeight(10)
        sidebar.addWidget(spacer)

        sidebar.addWidget(self.button4)
        spacer = QLabel()
        spacer.setFixedHeight(10)
        sidebar.addWidget(spacer)

        sidebar.addWidget(self.button5)
        spacer = QLabel()
        spacer.setFixedHeight(10)
        sidebar.addWidget(spacer)

        sidebar.addWidget(self.button6)

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

        self.button1.clicked.connect(self.on_button1_clicked)
        self.button2.clicked.connect(self.on_button2_clicked)
        self.button3.clicked.connect(self.on_button3_clicked)
        self.button4.clicked.connect(self.on_button4_clicked)
        self.button5.clicked.connect(self.on_button5_clicked)
        self.button6.clicked.connect(self.on_button6_clicked)



    def check_condition(self, button3, button4, button5, button6):
        """
            Cette partie sert à confirmer l'accès au chanels ainsi si la condition passe à True alors,
            le bouton devient visible.
        """
        if button3:
            self.button3.setVisible(True)
        else:
            self.button3.setVisible(False)
        if button4:
            self.button4.setVisible(True)
        else:
            self.button4.setVisible(False)
        if button5:
            self.button5.setVisible(True)
        else:
            self.button5.setVisible(False)
        if button6:
            self.button6.setVisible(True)
        else:
            self.button6.setVisible(False)



    """
        Nous avons la toutes les conditions lorsque nous appuyons sur les boutons.
    """
    def on_button1_clicked(self):
        """
            Lorsque le bouton 1 soit message privé est appuyer, il envoie au serveur "get_users_list".
            C'est le signal pour que le serveur lui envoie la liste des personnes inscrite à l'application.
            Ensuite après avoir reçu et split on crée un bouton par personne et lorsque l'on clique dessus,
            cela crée un chat area.
        """
        try:
            self.clear_chat_area()
            self.client_socket.send("get_users_list".encode())
            personnes_to_talk = self.client_socket.recv(1024).decode()
            users_list = personnes_to_talk.split(",")

            for user in users_list:
                user_button = QPushButton(user)
                user_button.clicked.connect(lambda checked, name=user: self.on_dynamic_button_clicked(name))
                self.add_user_button(user_button)

        except ConnectionResetError:
            print("Connexion réinitialisée par le serveur")
        except OSError:
            print("Erreur OS lors de la réception")
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")

    def add_user_button(self, button):
        button.clicked.connect(self.on_dynamic_button_clicked)
        self.chat.addWidget(button)

    def on_dynamic_button_clicked(self, name):
        print(f"Clicked on {name}")

    """
        À partir d'ici ce sont les boutons de chanels. Mon but est que lorsque l'on appuie sur un bouton.
        Cela ouvre une chat area, mais cela garde en mémoire le bouton et lorsque l'on envoie le message.
        Le destinataire devient la variable enregistrée avant. (room_name)
    """

    def on_button2_clicked(self):
        room_name = "Général"
        self.on_send_clicked(room_name)

    def on_button3_clicked(self):
        room_name = "Blabla"
        self.on_send_clicked(room_name)

    def on_button4_clicked(self):
        room_name = "Comptabilité"
        self.on_send_clicked(room_name)

    def on_button5_clicked(self):
        room_name = "Informatique"
        self.on_send_clicked(room_name)


    def on_button6_clicked(self):
        room_name = "Marketing"
        self.on_send_clicked(room_name)



    def on_disconnect_clicked(self):
        """
            Le bouton de déconnexion
        """
        print("Déconnecté")
        self.close_app_signal.emit()
        self.client_socket.close()



    def on_send_clicked(self, room_name):
        """
            Le bouton avec lequel on envoie des messages cela met "destinataire,message" et l'envoie au
            serveur qui lui le renvoie à tous les clients.
        """
        message_text = self.message_input.text()
        self.message_input.clear()
        self.add_text_to_chat_area(f"You: {message_text}")

        try:
            message_send = f"{room_name}/{message_text}"
            self.client_socket.send(message_send.encode())
        except ConnectionAbortedError:
            print("Le serveur n'est pas connecté")
        except ConnectionResetError:
            print("La connexion a été réinitialisée")
        except OSError:
            print("Erreur lors de l'envoi du message")



    def clear_chat_area(self):
        """
            Cette fonction sert comme son nom l'indique a clear le chat pour faire genre, on change de fenêtre.
        """
        while self.chat.count():
            child = self.chat.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


    def add_text_to_chat_area(self, text):
        """
            Cette fonction sert à ajouter des textes dans l'interface du client.
        """
        label = QTextEdit(self)
        label.setPlainText(text)
        label.setReadOnly(True)
        self.chat.addWidget(label)


def main():
    """
        Enfin la partie principale le main qui sert à rentrer en contact avec le serveur.
        Et lance aussi le Login pour débuter la boucle.
    """
    ip_address = "127.0.0.1"
    port = 1507
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip_address, port))

    app = QApplication([])

    login_window = LOGIN(client_socket)
    login_window.show()
    login_window.close_login_window_signal.connect(login_window.close)

    app.exec()


if __name__ == "__main__":
    main()
