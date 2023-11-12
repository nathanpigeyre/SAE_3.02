import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            reply = client_socket.recv(1024).decode()
            if not reply:
                print("Connexion perdue avec le serveur")
                break
            print(reply)
        except ConnectionResetError:
            print("Connexion perdue avec le serveur")
            break

def main():
    host = "127.0.0.1"
    port = 1501

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # Inscription
    username = input("Ton Nom: ")
    client_socket.send(username.encode())
    registration_status = client_socket.recv(1024).decode()
    print(registration_status)

    if "succès" in registration_status:
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()

        while True:
            message_send = input("You: ")
            try:
                client_socket.send(message_send.encode())
            except ConnectionAbortedError:
                print("Le serveur n'est pas connecté")
                break

if __name__ == "__main__":
    main()
