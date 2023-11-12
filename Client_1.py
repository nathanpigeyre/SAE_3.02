import socket
import threading

def receive_messages(client_socket):
    Connected = True
    while Connected == True:
        try:
            reply = client_socket.recv(1024).decode()
            if not reply:
                print("Connexion perdue avec le serveur")
                break
            print("\nMessage (autre Client): " + reply)
        except ConnectionResetError:
            print("Connexion perdue avec le serveur")
            break

def main():
    host = "127.0.0.1"
    port = 1501

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Connected = True
    while Connected == True:
        try:
            client_socket.connect((host, port))
            print("Connecté au serveur")
            receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
            receive_thread.start()
            break
        except ConnectionRefusedError:
            print("Le serveur n'est pas connecté")
        except OSError:
            break

    while Connected == True:
        message_send = str(input("Vous : "))
        try:
            client_socket.send(message_send.encode())
        except ConnectionAbortedError:
            print("Le serveur n'est pas connecté")
            break

if __name__ == "__main__":
    main()
