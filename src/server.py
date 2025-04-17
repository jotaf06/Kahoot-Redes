import socket
import threading

MAX_CONECTIONS = 5

#Criando o socket do servidor com IPv4 e protocolo TCP
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Cria um novo socket, AF_INET indica que é IPv4, SOCK_STREAM indica que é um socket TCP
servidor.bind(("localhost", 12345)) #"bind" liga o socket ao endereço e porta do servidor. Localhost é o endereço da maquina local e 12345 indica a porta que o servidor vai escutar
servidor.listen(MAX_CONECTIONS) #Coloca o servidor em escuta para até MAX_CONECTIONS conexões (clients)

clients =[] #Lista para armazenar os clientes conectados
nicknames = {} #Dicionário para armazenar os nicknames dos clientes

#Função que envia a mensagem para todos os clientes conectados
def broadcast(msg, src):
    for client in clients: # Para cada cliente na lista de clientes (percorre por todos os clientes conectados)
        if client != src: # Se o cliente não for o mesmo que enviou a mensagem (src)
            try:
                client.send(msg.encode("utf-8")) # Envia a mensagem para os clientes
            except:
                client.close() #Se der algum erro, fecha a conexão com o cliente
                if client in clients:
                    clients.remove(client) #remove o cliente da lista clients

#Função que trata as mensagens dos clientes
def handle_client(client):
        try:
            nick = client.recv(1024).decode("utf-8") #Espera uma mensagem do cliente de até 1Kb (1024 bytes)
            nicknames[client] = nick #Adiciona o nickname do cliente ao dicionário nicknames
            print(f"{nick} entrou na sala!") #Imprime uma mensagem indicando que o cliente entrou
            msg = f"{nick} entrou na sala!" #Mensagem de boas-vindas
            broadcast(msg, client) #Envia a mensagem para todos os clientes, exceto o proprio cliente que esta enviando

            while True:
                msg = client.recv(1024).decode("utf-8") #Espera uma mensagem do cliente de até 1Kb (1024 bytes)
                if msg.lower() == "/sair":
                    print(f"{nick} saiu do chat!") #Imprime uma mensagem indicando que o cliente saiu
                    broadcast(f"{nick} saiu do chat!", client) #envia um aviso para todos os clientes e remove o client do chat
                    break
                print(f"{nick}: {msg}") #Imprime a mensagem do cliente
                broadcast(f"{nick}: {msg}", client) #Envia a mensagem para todos os clientes indicando quem enviou

        except:
            try:
                clients.remove(client)
            except ValueError:
                pass
            client.close()

        if client in clients:
            clients.remove(client) #Se ocorrer um erro ao receber a mensagem, remove o cliente da lista
            del nicknames[client] #Remove o nickname do dicionário
        client.close() #Fecha a conexão com o cliente

if __name__ == "__main__":
    print(f"Servidor escutando na porta 12345\n")
    try:
        while True:
            client, addr = servidor.accept() #Aceita uma nova conexão
            print(f"Conectado com {addr}") #Imprime o endereço do cliente que se conectou
            clients.append(client) #Adiciona o novo cliente a lista de clientes

            thread = threading.Thread(target=handle_client, args=(client,)) #Cria uma nova thread para lidar com o cliente
            thread.start() #Inicia a thread
    except KeyboardInterrupt: #Se o usuario interromper a execucao por meio de ctrl C, o servidor é fechado.
        print("\nEncerrando servidor...\n")
        servidor.close()
        print("Servidor encerrado.")
