import socket
import threading
import sys

HOST = 'localhost'
PORT = 12345

def receive_loop(sock):
    while True:
        try:
            msg = sock.recv(4096).decode('utf-8')
            if not msg:
                break
            print(msg)
        except:
            break

if __name__ == "__main__":
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((HOST, PORT))

    nick = input("Seu nickname: ")
    cliente.send(nick.encode('utf-8'))

    # Thread para receber tudo do servidor
    threading.Thread(target=receive_loop, args=(cliente,), daemon=True).start()

    # Loop de envio (respostas)
    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            cliente.send(line.strip().encode('utf-8'))
    except KeyboardInterrupt:
        pass
    finally:
        cliente.close()
        print("Desconectado.")
