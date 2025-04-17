import socket
import threading

clients = []

def handle_client(client_socket, addr):
    print(f"[+] Novo cliente conectado: {addr}")
    client_socket.send("Bem-vindo ao WebChat!".encode())

    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if not msg:
                break
            print(f"[{addr}] {msg}")
            broadcast(msg, client_socket)
        except:
            break

    print(f"[-] Cliente {addr} desconectado")
    clients.remove(client_socket)
    client_socket.close()

def broadcast(message, source_socket):
    for client in clients:
        if client != source_socket:
            try:
                client.send(message.encode())
            except:
                client.close()
                clients.remove(client)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 5555))
    server.listen()
    print("[*] Servidor rodando em localhost:5555")

    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    main()
