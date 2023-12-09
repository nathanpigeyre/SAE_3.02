import socket
import threading
import mysql.connector

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
    Connection = True
    while Connection == True:
        if accepting_connections == False:
            break
        commande = input("Une Commande ? yes or no : ")
        if commande == "yes":
            choix = input("Kill or Kick or Ban : ")

            if choix == "Kick":
                Kick = input('Le nom ou adresse a Kick : ')
                # suppr de la databases et le rejouté dans un certain temps


            elif choix == "Ban":
                Ban = input('Le nom ou adresse a Ban : ')
                try:
                    cursor.execute("DELETE FROM users WHERE nom = %s", (Ban,))
                    db.commit()
                    if cursor.rowcount == 0:
                        print("Aucune entrée correspondant à '{}' à supprimer.".format(Ban))
                    else:
                        print("Suppression effectuée avec succès.")
                        client_socket.send("{}".format(Ban).encode())
                except mysql.connector.Error as err:
                    print("Erreur lors de la suppression : {}".format(err))



            elif choix == "Kill":
                print("Vous arrêtez votre serveur.")
                Kill = 'Kill'
                client_socket.send("{}".format(Kill).encode())
                accepting_connections = False
                break
            else:
                print("Il faut écrire Kill, Kick ou Ban")
        else:
            print("Vous avez écrit 'no' ou une mauvaise syntaxe")
            break
    client_socket.close()
def Server(client_socket):
    global accepting_connections
    id = client_socket.recv(1024).decode()
    password = client_socket.recv(1024).decode()

    cursor.execute("INSERT INTO users (nom, password, ip_address) VALUES (%s, %s, %s)", (id, password, client_socket.getpeername()[0]))
    db.commit()

    client_socket.send("Enregistrement est un succès. Vous pouvez envoyer des messages.".encode())
    print("Bienvenue à toi : {}".format(id))

    clients[client_socket] = id

    threading.Thread(target=server_commandes, args=(client_socket,)).start()


    global accepting_connections

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
            cursor.execute("INSERT INTO messages (envoyeur, receveur, message) VALUES (%s, %s, %s)",
                           (id, envoyeur, message_rec))
            db.commit()
            for socket, name in clients.items():
                if socket != client_socket:
                    try:
                        socket.send("\n")
                        socket.send("{}: {}".format(id, message_rec).encode())
                    except ConnectionResetError:
                        pass

        except ConnectionResetError:
            print("{} disconnected".format(id))
            cursor.execute("DELETE FROM users WHERE nom = %s", (id,))
            db.commit()
            del clients[client_socket]
            break
        except TypeError:
            break
        except ConnectionAbortedError:
            break
    client_socket.close()
    if not accepting_connections:
        client_socket.close()

def main():
    ip_address = "127.0.0.1"
    port = 1504

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip_address, port))
    server_socket.listen(5)
    print("Le Serveur écoute {}:{}".format(ip_address, port))

    global accepting_connections

    while accepting_connections:
        if not stop_server:
            client_socket, client_address = server_socket.accept()
            print("Accepte la connection de {}".format(client_address[0]))

            threading.Thread(target=Server, args=(client_socket,)).start()

        if stop_server:
            break
    server_socket.close()

    print("Serveur arrêté.")

if __name__ == "__main__":
    main()
