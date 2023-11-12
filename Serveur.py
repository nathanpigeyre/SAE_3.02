import socket
import threading

clients = []
def main():
    host = "127.0.0.1"
    port = 1500


    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("Le Serveur écoute {}:{}".format(host, port))

    Connected = True

    while Connected == True:
        client_socket, client_address = server_socket.accept()
        print("Accepte la connection de  {}".format(client_address[0]))
        clients.append(client_socket)
        client_thread = threading.Thread(target=server, args=(client_socket,))
        client_thread.start()

def server(server_socket):
    Connected = True
    while Connected == True:
        try:
            message_receve = server_socket.recv(1024).decode()
            if not message_receve:
                Connected = False
            print("\nMessage (autre Client): " + message_receve)
            
            for pointeur in clients:
                    if pointeur != server_socket:
                        try:
                            pointeur.send(message_receve.encode())
                        except ConnectionResetError:
                            pass
        except ConnectionResetError:
            break
        except ConnectionAbortedError:
            break
        except OSError:
            exit()
        except AttributeError:
            exit()





if __name__ == "__main__":
    main()