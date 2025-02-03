import socket
import threading
import json

class Server():
    def __init__(self, host="localhost", port=9000):
        self.__clients = []

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)
        print(f"Listening on {host}:{port}")
        
        while True:
            client, address = self.socket.accept()

            # add client to the list of clients
            self.__clients.append(client)

            print(f"Connection from {address}")
            
            message = client.recv(1024)
            print(f"Message sent from client {message.decode()}")
            try:
                message = json.loads(message.decode())
                client_thread = threading.Thread(target=self.handle_client, args=(client, message["user"]["name"]))
                client_thread.start()
            except json.decoder.JSONDecodeError:
                pass

    def handle_client(self, client, username):
        try:
            while True:
                # Read data from the client
                data = client.recv(1024)
                if not data: 
                    break
                print(f"Data gotten from client {data.decode()}")

                for sock in self.__clients:
                    if sock == client:
                        continue
                    sock.send(data)
                    
        except ConnectionResetError:
            pass
        finally:
            client.close()
            print(f"{username}'s socket closed")
            self.__clients.remove(client)


    def add_client_to_list(self, client):
        self.__clients.append(client)

    def remove_client_from_list(self, client):
        index = index(client)

        client = self.__clients.pop(index)

    def broadcast(msg, sender):
        pass

if __name__ == "__main__":
    server = Server()