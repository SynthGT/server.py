import socket
import threading
from cryptography.fernet import Fernet

# Generate encryption key if it doesn't already exist
try:
    with open("secret.key", "rb") as key_file:
        encryption_key = key_file.read()
except FileNotFoundError:
    encryption_key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(encryption_key)

# Initialize the cipher
cipher = Fernet(encryption_key)

# Server data
clients = {}
message_history = []

def handle_client(client_socket, addr):
    # Send encryption key to the client
    client_socket.send(encryption_key)
    
    client_socket.send(cipher.encrypt("Welcome to the chat! Enter your username:".encode()))
    username = cipher.decrypt(client_socket.recv(1024)).decode()
    clients[client_socket] = username
    print(f"[NEW CONNECTION] {username} connected.")

    while True:
        try:
            message = cipher.decrypt(client_socket.recv(1024)).decode()
            print(f"{username}: {message}")
            broadcast(f"{username}: {message}", client_socket)
        except:
            print(f"[DISCONNECT] {username}")
            del clients[client_socket]
            client_socket.close()
            break

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            client.send(cipher.encrypt(message.encode()))

# Start the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 12345))
server.listen()
print("[SERVER STARTED] Waiting for connections...")

while True:
    client_socket, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(client_socket, addr))
    thread.start()
