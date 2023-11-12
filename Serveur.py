import socket
import threading

clients = {}
nom = set()

def main():
    host = "127.0.0.1"
    port = 1501

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("Le Serveur écoute {}:{}".format(host, port))
    Connected = True
    while Connected == True:
        client_socket, client_address = server_socket.accept()
        print("Accepte la connection de {}".format(client_address[0]))
        threading.Thread(target=Server, args=(client_socket,)).start()

def Server(client_socket):
    id = client_socket.recv(1024).decode()
    if id in nom:
        client_socket.send("Username already taken. Disconnecting...".encode())
        client_socket.close()
        return
    else:
        nom.add(id)
        clients[client_socket] = id
        client_socket.send("Registration successful. You can now send messages.".encode())
        print("Bienvenue à {}".format(id))
    Connected = True
    while Connected == True:
        try:
            message_receive = client_socket.recv(1024).decode()
            if not message_receive:
                break

            print("\n{} : {}".format(id, message_receive))

            for socket, name in clients.items():
                if socket != client_socket:
                    try:

                        socket.send("\n".encode())
                        socket.send("{}: {}".format(id, message_receive).encode())
                    except ConnectionResetError:
                        pass
        except ConnectionResetError:
            print("{} disconnected".format(id))
            nom.remove(id)
            del clients[client_socket]
            break

if __name__ == "__main__":
    main()
