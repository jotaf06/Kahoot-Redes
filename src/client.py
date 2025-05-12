import socket
import sys
import json
import select
import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("SERVER_IP", "localhost")
PORT = int(os.getenv("SERVER_PORT", 12345))

def main():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(f"Não foi possível conectar ao servidor {HOST}:{PORT}.")
        sys.exit(1)

    nick = input("Digite seu nickname: ")
    cliente.send(nick.encode('utf-8'))

    quiz_ativo = False

    while True:
        sockets_list = [sys.stdin, cliente]
        read_sockets, _, _ = select.select(sockets_list, [], [], 0.1)

        for sock in read_sockets:
            if sock == cliente:
                try:
                    msg = sock.recv(4096).decode('utf-8')
                    if not msg:
                        continue
                    
                    data = json.loads(msg)
                    
                    if data.get('type') == 'question':
                        quiz_ativo = True
                        print(f"\nPergunta: {data['question']}")
                        for i, option in enumerate(data['options'], 1):
                            print(f"{i}. {option}")
                        print("Escolha sua resposta (1-4): ", end='', flush=True)
                    
                    elif data.get('type') == 'feedback':
                        quiz_ativo = False
                        print(f"\nResposta correta: {data['correct'] + 1}")
                        print("Pontuações atualizadas:")
                        for nick, score in data['scores'].items():
                            print(f"{nick}: {score}")
                        print("\nDigite mensagens ou /sair: ", end='', flush=True)
                    
                    else:
                        print(f"\n{msg}")
                
                except json.JSONDecodeError:
                    print(f"\nMensagem do servidor: {msg}")
            
            else:
                line = sys.stdin.readline().strip()
                if quiz_ativo:
                    cliente.send(line.encode('utf-8'))
                    quiz_ativo = False
                else:
                    if line.lower() == '/sair':
                        cliente.send(line.encode('utf-8'))
                        print("Desconectando...")
                        cliente.close()
                        return
                    else:
                        cliente.send(line.encode('utf-8'))

        if not read_sockets:
            continue

if __name__ == "__main__":
    main()