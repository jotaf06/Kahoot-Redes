import socket
import threading

def receber_mensagens(sock):
    while True:
        try:
            mensagem = sock.recv(1024)
            if not mensagem:
                break
            print("Mensagem recebida:", mensagem.decode())
        except:
            break

def main():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(('localhost', 5555))

    print(cliente.recv(1024).decode())

    # Thread para receber mensagens
    t = threading.Thread(target=receber_mensagens, args=(cliente,))
    t.start()

    # Envio de mensagens
    while True:
        msg = input()
        if msg.lower() == '/quit':
            break
        cliente.sendall(msg.encode())

    cliente.close()

if __name__ == '__main__':
    main()
