import socket
import threading
import mysql.connector
import datetime
import json


db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="toto",
    database="discord"
)
cursor = db.cursor()

clients = {}
accepting_connections = True
connection_lock = threading.Lock()
stop_server = False

def send_user_list(client_socket):
    try:
        cursor.execute("SELECT nom FROM users")
        users_list = [user[0] for user in cursor.fetchall()]
        users_str = ','.join(users_list)
        client_socket.send(users_str.encode())
    except mysql.connector.Error as err:
        print("Erreur lors de la récupération des utilisateurs depuis la base de données :", err)

def server_commandes(client_socket):
    global accepting_connections
    global stop_server
    global cursor

    while accepting_connections:
        if not stop_server:
            commande = input("Une Commande ? y or n : ")
            if commande == "y":
                choix = input("kill or kick or ban : ")

                if choix == "kick":
                    Kick = input('Le nom ou adresse a Kick : ')
                    timekick = int(input("Combien de temps (en minute) : "))
                    try:
                        cursor.execute("SELECT * FROM users WHERE nom = %s", (Kick,))
                        result = cursor.fetchall()
                        if len(result) == 0:
                            cursor.execute("SELECT nom FROM users WHERE ip_address = %s", (Kick,))
                            result_ip = cursor.fetchall()
                            if len(result_ip) == 0:
                                print("Aucune entrée correspondant à '{}'\n".format(Kick))
                            else:

                                for row in result_ip:
                                    name = row[0]
                                    cursor.execute("SELECT * FROM kick WHERE nom = %s", (name,))
                                    existing_kick = cursor.fetchone()

                                    if existing_kick:
                                        cursor.execute("UPDATE kick SET created_at = NOW(), temps_kick = %s WHERE nom = %s",(timekick, name))
                                        db.commit()
                                        print("Kick existant mis à jour pour '{}'.\n".format(name))
                                    else:
                                        cursor.execute("INSERT INTO kick (nom, created_at, temps_kick) VALUES (%s, NOW(), %s)",(name, timekick))
                                        db.commit()
                                        print("Le kick pour '{}' a été effectué avec succès.\n".format(name))
                                        client_socket.send("~{}:{}".format(name, timekick).encode())
                        else:
                            cursor.execute("INSERT INTO kick (nom, created_at, temps_kick) VALUES (%s, NOW(), %s)",(Kick, timekick))
                            db.commit()
                            print("Le kick a été effectué avec succès.\n")
                            client_socket.send("~{}:{}".format(Kick, timekick).encode())
                    except mysql.connector.Error as err:
                        print("Erreur lors du kick : {}\n".format(err))

                elif choix == "ban":
                    Ban = input('Le nom ou adresse a Ban : ')
                    try:
                        cursor.execute("DELETE FROM users WHERE nom = %s", (Ban,))
                        db.commit()
                        if cursor.rowcount == 0:
                            print("Aucune entrée correspondant à '{}'.\n".format(Ban))
                        else:
                            print("Le Ban a été effectuée avec succès.\n")
                            client_socket.send("!{}".format(Ban).encode())
                    except mysql.connector.Error as err:
                        print("Erreur lors de la suppression : {}\n".format(err))
                    except OSError as err:
                        print("Erreur lors de la suppression : {}\n".format(err))


                elif choix == "kill":
                    print("Vous arrêtez votre serveur.\n")
                    Kill = 'Kill'
                    client_socket.send("{}".format(Kill).encode())
                    client_socket.close()
                    stop_server = True
                    accepting_connections = False
                    break
                else:
                    print("Il faut écrire Kill, Kick ou Ban\n")
            else:
                print("Vous avez écrit 'no' ou une mauvaise syntaxe\n")
                pass


    client_socket.close()


def Server(client_socket):
    try:
        global accepting_connections
        id= ""
        logorsign = client_socket.recv(1024).decode()

        if logorsign == "!#sign":
            id = client_socket.recv(1024).decode()
            password = client_socket.recv(1024).decode()
            cursor.execute("SELECT * FROM users WHERE nom = %s", (id,))
            existing_user = cursor.fetchone()
            if existing_user:
                client_socket.send("Warning! L'identifiant existe déjà.".encode())
            else:
                if password == "!#sign":
                    client_socket.send("No password".encode())
                else:
                    cursor.execute("INSERT INTO users (nom, password, ip_address) VALUES (%s, %s, %s)",(id, password, client_socket.getpeername()[0]))
                    db.commit()
                    client_socket.send("Inscription réussie.".encode())
                    client_socket.send("Bienvenue à toi : {}\n".format(id).encode())

        elif logorsign == "!#log":
            id = client_socket.recv(1024).decode()
            password = client_socket.recv(1024).decode()
            cursor.execute("SELECT * FROM users WHERE nom = %s AND password = %s", (id, password))
            user = cursor.fetchone()

            if user:
                cursor.execute("SELECT temps_kick, created_at FROM kick WHERE nom = %s", (id,))
                kick_details = cursor.fetchone()
                if kick_details:
                    temps_kick, created_at = kick_details
                    now = datetime.datetime.now()
                    diff = (created_at + datetime.timedelta(minutes=temps_kick)) - now
                    if diff.total_seconds() <= 0:
                        client_socket.send("Connexion réussie.".encode())
                        cursor.execute("DELETE FROM kick WHERE nom = %s", (id,))
                        db.commit()

                    else:
                        if diff.total_seconds() < 60:
                            client_socket.send(f"Reconnexion interdite pour {round(diff.total_seconds())} secondes.".encode())
                        else:
                            temps_restant = int(diff.total_seconds() / 60)
                            client_socket.send(f"Reconnexion interdite pour {temps_restant} minutes.".encode())

                else:
                    client_socket.send("Connexion réussie.".encode())
                    client_socket.send("Bienvenue à toi : {}\n".format(id).encode())
            else:
                client_socket.send("Identifiants invalides. Veuillez réessayer.".encode())
        clients[client_socket] = id

        connection_lock.acquire()
        if accepting_connections:
            clients[client_socket] = id
        else:
            client_socket.close()
            connection_lock.release()
            return
        connection_lock.release()
        cursor.execute("SELECT Blabla, Comptabilite, Informatique, Marketing FROM users WHERE nom = %s", (id,))
        user_channels = cursor.fetchone()
        droits = []
        if user_channels:
            if user_channels[0]:
                droits.append("Blabla")
            if user_channels[1]:
                droits.append("Comptabilite")
            if user_channels[2]:
                droits.append("Informatique")
            if user_channels[3]:
                droits.append("Marketing")

        droits_json = json.dumps(droits)
        json_droits = '%' + id + '/' + droits_json
        client_socket.send(json_droits.encode())
        Connected = True
        while Connected == True:
            try:

                message_receive = client_socket.recv(1024).decode()
                if not message_receive:
                    break
                if message_receive == "get_users_list":
                    send_user_list(client_socket)

                if message_receive.startswith('%!§'):
                    message_select = message_receive.replace('%!§', '')
                    mots = message_select.split(',')
                    for mot in mots:
                        if "Blabla" == mot:
                            cursor.execute("UPDATE users SET Blabla = 1 WHERE nom = %s", (id,))
                            db.commit()
                        elif "Comptabilite" == mot:
                            cursor.execute("UPDATE users SET Comptabilite = 1 WHERE nom = %s", (id,))
                            db.commit()
                        elif "Informatique" == mot:
                            cursor.execute("UPDATE users SET Informatique = 1 WHERE nom = %s", (id,))
                            db.commit()
                        elif "Marketing" == mot:
                            cursor.execute("UPDATE users SET Marketing = 1 WHERE nom = %s", (id,))
                            db.commit()

                else:
                    message_databases = message_receive.split("/")
                    if len(message_databases) >= 2:
                        room_or_recipient = message_databases[0]
                        message_rec = message_databases[1]


                        cursor.execute("INSERT INTO messages (envoyeur, receveur, message) VALUES (%s, %s, %s)",(id, room_or_recipient, message_rec))
                        db.commit()


                        for socket, name in clients.items():
                            if name == room_or_recipient:
                                try:
                                    socket.send("{}: {}".format(id, message_rec).encode())
                                except ConnectionResetError:
                                    pass

                cursor.execute("SELECT Blabla, Comptabilite, Informatique, Marketing FROM users WHERE nom = %s", (id,))
                user_channels = cursor.fetchone()
                droits = []
                if user_channels:
                    if user_channels[0]:
                        droits.append("Blabla")
                    if user_channels[1]:
                        droits.append("Comptabilite")
                    if user_channels[2]:
                        droits.append("Informatique")
                    if user_channels[3]:
                        droits.append("Marketing")

                droits_json = json.dumps(droits)
                json_droits = '%' + id + '/' + droits_json
                client_socket.send(json_droits.encode())


            except ConnectionResetError:
                print("{} s'est déconnecter\n".format(id))
                del clients[client_socket]
                client_socket.close()
                break
            except TypeError:
                break
            except ConnectionAbortedError:
                break
        client_socket.close()
        if not accepting_connections:
            client_socket.close()
    except ConnectionAbortedError:
        client_socket.close()
    except ConnectionResetError:
        client_socket.close()

def main():
    ip_address = "127.0.0.1"
    port = 1507

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip_address, port))
    server_socket.listen(5)
    print("Le Serveur écoute {}:{}\n".format(ip_address, port))

    global accepting_connections
    global stop_server

    while accepting_connections:
        if not stop_server:
            client_socket, client_address = server_socket.accept()
            print("Accepte la connection de {}\n".format(client_address[0]))

            threading.Thread(target=Server, args=(client_socket,)).start()
            threading.Thread(target=server_commandes, args=(client_socket,)).start()
        if stop_server:
            break
    server_socket.close()
    print("Serveur arrêté.\n")

if __name__ == "__main__":
    main()
