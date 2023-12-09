import socket
import threading
import mysql.connector
import datetime

# Connexion à la base de données
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

def server_commandes(client_socket):
    global accepting_connections
    global stop_server
    global cursor

    while accepting_connections:
        if not stop_server:
            commande = input("Une Commande ? yes or no : ")
            if commande == "yes":
                choix = input("Kill or Kick or Ban : ")

                if choix == "Kick":
                    Kick = input('Le nom ou adresse a Kick : ')
                    timekick = int(input("Combien de temps (en minute) : "))
                    try:
                        cursor.execute("SELECT * FROM users WHERE nom = %s", (Kick,))
                        result = cursor.fetchall()
                        if len(result) == 0:
                            cursor.execute("SELECT nom FROM users WHERE ip_address = %s", (Kick,))
                            result_ip = cursor.fetchall()
                            if len(result_ip) == 0:
                                print("Aucune entrée correspondant à '{}'".format(Kick))
                            else:

                                for row in result_ip:
                                    name = row[0]
                                    cursor.execute("SELECT * FROM kick WHERE nom = %s", (name,))
                                    existing_kick = cursor.fetchone()

                                    if existing_kick:
                                        cursor.execute("UPDATE kick SET created_at = NOW(), temps_kick = %s WHERE nom = %s",(timekick, name))
                                        db.commit()
                                        print("Kick existant mis à jour pour '{}'.".format(name))
                                    else:
                                        cursor.execute("INSERT INTO kick (nom, created_at, temps_kick) VALUES (%s, NOW(), %s)",(name, timekick))
                                        db.commit()
                                        print("Le kick pour '{}' a été effectué avec succès.".format(name))
                                        client_socket.send("~{}:{}".format(name, timekick).encode())
                        else:
                            cursor.execute("INSERT INTO kick (nom, created_at, temps_kick) VALUES (%s, NOW(), %s)",(Kick, timekick))
                            db.commit()
                            print("Le kick a été effectué avec succès.")
                            client_socket.send("~{}:{}".format(Kick, timekick).encode())
                    except mysql.connector.Error as err:
                        print("Erreur lors du kick : {}".format(err))

                elif choix == "Ban":
                    Ban = input('Le nom ou adresse a Ban : ')
                    try:
                        cursor.execute("DELETE FROM users WHERE nom = %s", (Ban,))
                        db.commit()
                        if cursor.rowcount == 0:
                            print("Aucune entrée correspondant à '{}'.".format(Ban))
                        else:
                            print("Le Ban a été effectuée avec succès.")
                            client_socket.send("!{}".format(Ban).encode())
                    except mysql.connector.Error as err:
                        print("Erreur lors de la suppression : {}".format(err))


                elif choix == "Kill":
                    print("Vous arrêtez votre serveur.")
                    Kill = 'Kill'
                    client_socket.send("{}".format(Kill).encode())
                    client_socket.close()
                    stop_server = True
                    accepting_connections = False
                    break
                else:
                    print("Il faut écrire Kill, Kick ou Ban")
            else:
                print("Vous avez écrit 'no' ou une mauvaise syntaxe")
                pass


    client_socket.close()


def Server(client_socket):
    try:
        global accepting_connections
        id= ""
        logorsign = client_socket.recv(1024).decode()

        if logorsign == "sign":
            id = client_socket.recv(1024).decode()
            password = client_socket.recv(1024).decode()
            cursor.execute("INSERT INTO users (nom, password, ip_address) VALUES (%s, %s, %s)", (id, password, client_socket.getpeername()[0]))
            db.commit()
            client_socket.send("Inscription réussie.".encode())
            print("Bienvenue à toi : {}".format(id))

        elif logorsign == "log":
            id = client_socket.recv(1024).decode()

            password = client_socket.recv(1024).decode()
            print(password)
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
                    print("Bienvenue à toi : {}".format(id))
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

        Connected = True
        while Connected == True:
            try:
                message_receive = client_socket.recv(1024).decode()
                if not message_receive:
                    break

                message_databases = message_receive.split("/")
                message_rec = message_databases[1]
                envoyeur = message_databases[0]
                print("{} : {}".format(id, message_rec))
                cursor.execute("INSERT INTO messages (envoyeur, receveur, message) VALUES (%s, %s, %s)",(id, envoyeur, message_rec))
                db.commit()
                for socket, name in clients.items():
                    if socket != client_socket:
                        try:
                            socket.send("{}: {}".format(id, message_rec).encode())
                        except ConnectionResetError:
                            pass


            except ConnectionResetError:
                print("{} disconnected".format(id))
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
    port = 1506

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip_address, port))
    server_socket.listen(5)
    print("Le Serveur écoute {}:{}".format(ip_address, port))

    global accepting_connections
    global stop_server

    while accepting_connections:
        if not stop_server:
            client_socket, client_address = server_socket.accept()
            print("Accepte la connection de {}".format(client_address[0]))

            threading.Thread(target=Server, args=(client_socket,)).start()
            threading.Thread(target=server_commandes, args=(client_socket,)).start()
        if stop_server:
            break
    server_socket.close()
    print("Serveur arrêté.")

if __name__ == "__main__":
    main()
