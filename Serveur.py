import socket
import threading
import mysql.connector

db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="toto",
    database="discord"
)

cursor = db.cursor()

clients = {}

def main():
    ip_address = "127.0.0.1"
    port = 1503

    #Connected = True
    #while Connected == True:
        #usernameroot = input("Ton Nom: ")
        #passwordroot = input("Ton Mot de Passe: ")
        #if usernameroot == "root" and passwordroot == "root":
            #Connected = False
        #else:
            #print("Votre mot de passe ou votre nom d'utilisateur est éronné")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip_address, port))
    server_socket.listen(5)
    print("Le Serveur écoute {}:{}".format(ip_address, port))

    Connected = True
    while Connected == True:
        client_socket, client_address = server_socket.accept()
        print("Accepte la connection de {}".format(client_address[0]))

        threading.Thread(target=Server, args=(client_socket,)).start()

def Server(client_socket):
    id = client_socket.recv(1024).decode()
    password = client_socket.recv(1024).decode()


    cursor.execute("INSERT INTO users (nom, password, ip_address) VALUES (%s, %s, %s)", (id, password, client_socket.getpeername()[0]))
    db.commit()

    client_socket.send("Enregistrement est un succès. Vous pouvez envoyer des messages.".encode())
    print("Bienvenue a toi : {}".format(id))

    clients[client_socket] = id

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


if __name__ == "__main__":
    main()
