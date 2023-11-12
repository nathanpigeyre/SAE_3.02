import socket
import threading

def receive_messages(client_socket):
    Connected = True
    while Connected == True:
        try:
            reply = client_socket.recv(1024).decode()
            if not reply:
                Connected = False
            print("\nMessage (autre Client): " + reply)
        except ConnectionResetError:
            break
def main():
    host = "127.0.0.1"
    port = 1500
    Boucle = True
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while Boucle == True:
        Connected = False
        while Connected == False:
            try:
                client_socket.connect((host, port))
            except ConnectionRefusedError:
                print("Le Server n'est pas connecté")
            except OSError:
                break
            else:
                Connected = True
                print("Connecter au serveur")
                receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
                receive_thread.start()
        if Connected == True:
            message_send = str(input("Vous : "))
            try:
                client_socket.send(message_send.encode())
            except ConnectionAbortedError:
                print("Le serveur n'est pas connecté")
                connected = False
            else:
                print("")#pas encore fait


if __name__ == "__main__":
    main()

