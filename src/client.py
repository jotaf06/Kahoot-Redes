import socket
import threading
import sys

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Cria um novo socket, AF_INET indica que é IPv4, SOCK_STREAM indica que é um socket TCP
cliente.connect(("localhost", 12345)) #Conecta ao servidor na porta 12345

nickname = input("Digite seu apelido no chat: ") #Solicita ao usuario o nickname dele
cliente.send(nickname.encode('utf-8')) #envia o nickname para o servidor

#Função que recebe as mensagens do servidor
def receive():
    while True:
        try:
            msg = cliente.recv(1024).decode('utf-8') #Recebe a mensagem do servidor
            print(msg) #Imprime a mensagem
        except:
            print("Ocorreu um erro ao receber a mensagem") #Imprime uma mensagem de erro
            cliente.close() #Fecha a conexão com o servidor
            break

#Função que envia as mensagens para o servidor
def send_msg():
    while True:
        try:
            msg = input()
            cliente.send(msg.encode('utf-8'))

            if msg.strip().lower() == "/sair":
                print("\nDesconectando do servidor...")
                cliente.close()
                sys.exit()

        except (KeyboardInterrupt, BrokenPipeError):
            print("\nDesconectado do servidor.")
            try:
                cliente.send("/sair".encode('utf-8'))
            except:
                pass
            cliente.close()
            sys.exit()

        except Exception as e:
            print(f"Erro inesperado: {e}")
            cliente.close()
            sys.exit()


if __name__ == "__main__":
    receive_thread = threading.Thread(target=receive) #Cria uma nova thread para receber as mensagens
    receive_thread.start() #Inicia a thread

    send_msg()

