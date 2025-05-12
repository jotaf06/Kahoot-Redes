import socket
import threading
import os
import json
import time
from dotenv import load_dotenv
from threading import Lock

load_dotenv()

SERVER_IP = os.getenv("SERVER_IP", "localhost")
SERVER_PORT = int(os.getenv("SERVER_PORT", 12345))
DATA_FILE = os.getenv("DATA_FILE", "../data/data.json")
HISTORY_FILE = os.getenv("HISTORY_FILE", "../data/history.json")

clients = []
nicknames = {}
partida_iniciada = threading.Event()
current_answers = {}
answers_lock = Lock()

history_lock = Lock()
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
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

def send_question_to_clients(question):
    question_data = {
        'type': 'question',
        'question': question['pergunta'],
        'options': question['opcoes']
    }
    for client in clients:
        client.send(json.dumps(question_data).encode('utf-8'))

def broadcast(msg, src=None):
    append_history(msg)
    for client in clients:
        if client != src:
            try:
                client.send(msg.encode("utf-8"))
            except:
                client.close()
                if client in clients:
                    clients.remove(client)

def handle_client(client):
    try:
        nick = client.recv(1024).decode("utf-8")
        nicknames[client] = nick
        broadcast(f"{nick} entrou na sala!", client)

        while True:
            msg = client.recv(1024).decode("utf-8")
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
        if client in clients:
            clients.remove(client)
        if client in nicknames:
            del nicknames[client]
        client.close()

def start_quiz():
    scores = {client: 0 for client in clients}
    for question in load_questions():
        send_question_to_clients(question)
        with answers_lock:
            current_answers.clear()
        start_time = time.time()
        timeout = 10
        expected_clients = clients.copy()
        while time.time() - start_time < timeout:
            with answers_lock:
                remaining = [c for c in expected_clients if c not in current_answers]
                if not remaining:
                    break
            time.sleep(0.1)
        correct = question['resposta']
        for client in clients:
            if client in current_answers:
                try:
                    chosen = int(current_answers[client]) - 1
                    if chosen == correct:
                        scores[client] += 1
                except ValueError:
                    pass
        feedback = {
            'type': 'feedback',
            'correct': correct,
            'scores': {nicknames[c]: scores[c] for c in clients}
        }
        for client in clients:
            client.send(json.dumps(feedback).encode('utf-8'))
        time.sleep(2)
    max_score = max(scores.values())
    winners = [c for c, s in scores.items() if s == max_score]
    winner_nicks = [nicknames[c] for c in winners]
    feedback_msg = f"Fim do quiz! Vencedor: {winner_nicks} com {max_score} pontos!" if len(winners) == 1 else f"Fim do quiz! Empate entre: {winner_nicks} com {max_score} pontos!"
    append_history(feedback_msg)
    broadcast(feedback_msg, None)
    partida_iniciada.clear()

def menu_servidor():
    print(f"\nServidor iniciado em {SERVER_IP}:{SERVER_PORT}")
    print("Comandos disponíveis:\n/sair - Encerra o servidor\n/iniciar - Inicia o quiz")
    while True:
        cmd = input(">> ").strip().lower()
        if cmd == "/sair":
            print("Encerrando servidor...")
            broadcast("Servidor foi encerrado.")
            for client in clients:
                client.close()
            servidor.close()
            os._exit(0)
        elif cmd == "/iniciar":
            if len(clients) >= 2:
                print("Iniciando quiz...")
                partida_iniciada.set()
                threading.Thread(target=start_quiz).start()
            else:
                print("É necessário pelo menos dois jogadores para iniciar o quiz.")
        else:
            print("Comando inválido. Use '/sair' ou '/iniciar'.")

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.bind((SERVER_IP, SERVER_PORT))
servidor.listen(5)

def aceitar_conexoes():
    while True:
        try:
            client, addr = servidor.accept()
            print(f"Conectado com {addr}")
            clients.append(client)
            threading.Thread(target=handle_client, args=(client,)).start()
        except OSError:
            break

if __name__ == "__main__":
    dir_path = os.path.dirname(HISTORY_FILE)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)

    menu_thread = threading.Thread(target=menu_servidor, daemon=True)
    menu_thread.start()
    aceitar_conexoes()
