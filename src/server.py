import socket
import threading
import json

HOST = 'localhost'
PORT = 12345
MAX_CLIENTS = 5

# Carrega perguntas do JSON
with open('../data/data.json', 'r', encoding='utf-8') as f:
    quiz = json.load(f)

clients = []
nicknames = {}

lock = threading.Lock()

def broadcast(msg):
    for c in clients:
        try:
            c.send(msg.encode('utf-8'))
        except:
            pass

def handle_client(client):
    # Recebe nickname
    nick = client.recv(1024).decode('utf-8')
    with lock:
        nicknames[client] = {'nick': nick, 'score': 0}
    client.send("Aguardando início do quiz...\n".encode('utf-8'))

    # Todos prontos? (simples: espera até MAX_CLIENTS)
    if len(nicknames) == MAX_CLIENTS:
        start_quiz()

def start_quiz():
    # Em cada pergunta:
    for idx, q in enumerate(quiz):
        texto = f"\nPergunta {idx+1}: {q['pergunta']}\n"
        for i, op in enumerate(q['opcoes']):
            texto += f"  {i}) {op}\n"
        texto += "Responda com o número da opção.\n"
        broadcast(texto)

        # coleta respostas
        respostas = {}
        for c in clients:
            try:
                ans = c.recv(1024).decode('utf-8').strip()
                respostas[c] = int(ans)
            except:
                respostas[c] = None

        # checa e pontua
        corretas = q['resposta']
        res_text = f"Resposta correta: {corretas}\n"
        for c, resp in respostas.items():
            if resp == corretas:
                with lock:
                    nicknames[c]['score'] += 1
                res_text += f"{nicknames[c]['nick']} acertou! +1 ponto\n"
            else:
                res_text += f"{nicknames[c]['nick']} errou.\n"
        broadcast(res_text)

    # Fim do quiz: envia placar
    placar = "\n--- Resultado Final ---\n"
    for info in nicknames.values():
        placar += f"{info['nick']}: {info['score']} pts\n"
    broadcast(placar)
    servidor.close()

if __name__ == "__main__":
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen(MAX_CLIENTS)
    print(f"Servidor iniciado em {HOST}:{PORT}")

    try:
        while True:
            client, addr = servidor.accept()
            print(f"{addr} conectado")
            clients.append(client)
            threading.Thread(target=handle_client, args=(client,), daemon=True).start()
    except KeyboardInterrupt:
        servidor.close()
        print("Servidor encerrado.")
