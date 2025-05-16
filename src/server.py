import socket
import threading
import os
import json
import time
from dotenv import load_dotenv
from threading import Lock

load_dotenv(override=True)

SERVER_IP      = os.getenv("SERVER_IP", "localhost")
SERVER_PORT    = int(os.getenv("SERVER_PORT", 12345))
DATA_FILE      = os.getenv("DATA_FILE", "../data/data.json")
HISTORY_FILE   = os.getenv("HISTORY_FILE", "../data/history.json")

print(f"[DEBUG] SERVER_IP: {SERVER_IP}")
print(f"[DEBUG] SERVER_PORT: {SERVER_PORT}")

clients        = []
nicknames      = {}
partida_iniciada = threading.Event()
current_answers  = {}
answers_lock     = Lock()
history_lock     = Lock()

def append_history(msg: str):
    with history_lock:
        try:
            with open(HISTORY_FILE, "r+", encoding="utf-8") as f:
                data = json.load(f)
                data.append(msg)
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.truncate()
        except (FileNotFoundError, json.JSONDecodeError):
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump([msg], f, ensure_ascii=False, indent=2)

def load_questions():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def send_question_to_clients(question):
    payload = {
        'type':    'question',
        'question':question['pergunta'],
        'options': question['opcoes']
    }
    for c in clients:
        c.send(json.dumps(payload).encode('utf-8'))

def broadcast(msg, src=None):
    append_history(msg)
    for c in clients:
        if c != src:
            try:
                c.send(msg.encode("utf-8"))
            except:
                c.close()
                clients.remove(c)

def handle_client(client):
    try:
        nick = client.recv(1024).decode('utf-8')
        nicknames[client] = nick

        # envia histórico
        with history_lock:
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                history = []
        client.send(json.dumps({'type':'history','messages':history}).encode('utf-8'))

        broadcast(f"{nick} entrou na sala!", client)

        while True:
            msg = client.recv(1024).decode('utf-8')
            if not msg:
                break

            if partida_iniciada.is_set():
                with answers_lock:
                    current_answers[client] = msg
                client.send("Resposta registrada!".encode('utf-8'))
            else:
                if msg.lower() == "/sair":
                    broadcast(f"{nick} saiu da sala.", client)
                    break
                broadcast(f"{nick}: {msg}", client)

    except Exception as e:
        append_history(f"Erro com {nick}: {e}")
    finally:
        if client in clients:    clients.remove(client)
        if client in nicknames:  del nicknames[client]
        client.close()

def start_quiz():
    scores = {c:0 for c in clients}
    for q in load_questions():
        send_question_to_clients(q)
        with answers_lock:
            current_answers.clear()
        start = time.time()
        timeout = 10
        while time.time() - start < timeout:
            with answers_lock:
                if len(current_answers) >= len(clients):
                    break
            time.sleep(0.1)

        correct = q['resposta']
        for c, ans in current_answers.items():
            try:
                if int(ans)-1 == correct:
                    scores[c] += 1
            except:
                pass

        fb = {
            'type':    'feedback',
            'correct': correct,
            'scores': {nicknames[c]:scores[c] for c in clients}
        }
        for c in clients:
            c.send(json.dumps(fb).encode('utf-8'))
        time.sleep(2)

    max_score = max(scores.values(), default=0)
    winners   = [c for c,s in scores.items() if s==max_score]
    winner_nicks = [nicknames[c] for c in winners]
    msg = (f"Fim do quiz! Vencedor: {winner_nicks} com {max_score} pontos!"
           if len(winners)==1
           else f"Fim do quiz! Empate entre {winner_nicks} com {max_score} pontos!")
    append_history(msg)
    broadcast(msg)
    partida_iniciada.clear()

def menu_servidor():
    print(f"Servidor em {SERVER_IP}:{SERVER_PORT}")
    print("Comandos: /iniciar, /sair")
    while True:
        cmd = input(">> ").strip().lower()
        if cmd == "/sair":
            broadcast("Servidor encerrado.")
            for c in clients: c.close()
            servidor.close()
            os._exit(0)
        elif cmd == "/iniciar":
            if len(clients) < 2:
                print("Precisam haver ao menos 2 jogadores.")
            else:
                partida_iniciada.set()
                threading.Thread(target=start_quiz, daemon=True).start()
        else:
            print("Comando inválido.")

# inicialização
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((SERVER_IP, SERVER_PORT))
servidor.listen(5)

if __name__ == "__main__":
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    # limpa histórico ao iniciar
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)

    threading.Thread(target=menu_servidor, daemon=True).start()
    print("Aguardando conexões...")
    while True:
        try:
            client, addr = servidor.accept()
            print(f"Conectado por {addr}")
            clients.append(client)
            threading.Thread(target=handle_client, args=(client,), daemon=True).start()
        except OSError:
            break
