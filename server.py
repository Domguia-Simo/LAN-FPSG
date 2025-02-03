import socket
import threading
import json

class GameServer:
    def __init__(self, host='', port=9000):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.clients = []
        self.players = {}  # Track connected players and their roles
        self.running = True
        print(f"Server initialized on {host}:{port}")

    def start(self):
        """Start the server and listen for connections"""
        try:
            self.server.listen(2)
            print(f"Server listening on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, addr = self.server.accept()
                    print(f"Client connected from {addr}")
                    self.clients.append(client_socket)
                    
                    # Start a new thread to handle this client
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except Exception as e:
                    print(f"Error accepting connection: {e}")
                    break
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()

    def handle_client(self, client_socket, addr):
        """Handle messages from a client"""
        try:
            # Wait for initial connection message
            data = client_socket.recv(1024).decode('utf-8')
            player_info = json.loads(data)
            self.players[client_socket] = player_info['user']
            print(f"Player connected: {player_info['user']['name']} as {player_info['user']['role']}")

            while self.running:
                try:
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                    
                    message = json.loads(data)
                    print(f"Forwarding message from {message['user']['role']}")
                    
                    # Broadcast to other clients
                    for other_client in self.clients:
                        if other_client != client_socket:
                            try:
                                other_client.send(data.encode('utf-8'))
                            except:
                                self.clients.remove(other_client)
                except:
                    break
        finally:
            if client_socket in self.players:
                del self.players[client_socket]
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_socket.close()
            print(f"Client {addr} disconnected")

    def stop(self):
        """Stop the server and close all connections"""
        self.running = False
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        self.server.close()
        print("Server stopped")

if __name__ == "__main__":
    server = GameServer()
    server.start()
