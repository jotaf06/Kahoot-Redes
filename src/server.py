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

clients = []
nicknames = {}
partida_iniciada = threading.Event()
current_answers = {}
answers_lock = Lock()

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
        print(f"{nick} entrou na sala.")
        broadcast(f"{nick} entrou na sala!", client)

        while True:
            msg = client.recv(1024).decode("utf-8")
            if partida_iniciada.is_set():
                with answers_lock:
                    current_answers[client] = msg
                client.send("Resposta registrada!".encode('utf-8'))
            else:
                if msg.lower() == "/sair":
                    print(f"{nick} saiu da sala.")
                    broadcast(f"{nick} saiu da sala.", client)
                    break
                print(f"{nick}: {msg}")
                broadcast(f"{nick}: {msg}", client)
    except Exception as e:
        print(f"Erro com {nick}: {e}")
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
                remaining = [client for client in expected_clients if client not in current_answers]
                if not remaining:
                    break
            time.sleep(0.1)
        
        correct = question['resposta']
        for client in clients:
            if client in current_answers:
                answer = current_answers[client]
                try:
                    chosen = int(answer) - 1
                    if chosen == correct:
                        scores[client] += 1
                except ValueError:
                    pass
        
        feedback = {
            'type': 'feedback',
            'correct': correct,
            'scores': {nicknames[client]: scores[client] for client in clients}
        }
        for client in clients:
            client.send(json.dumps(feedback).encode('utf-8'))
        time.sleep(2)
    
    max_score = max(scores.values())
    winners = [client for client, score in scores.items() if score == max_score]
    if len(winners) == 1:
        winner_nick = nicknames[winners[0]]
        broadcast(f"Fim do quiz! Vencedor: {winner_nick} com {max_score} pontos!", None)
    else:
        winner_nicks = ", ".join(nicknames[client] for client in winners)
        broadcast(f"Fim do quiz! Empate entre: {winner_nicks} com {max_score} pontos!", None)
    
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
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()
        except OSError:
            break

if __name__ == "__main__":
    menu_thread = threading.Thread(target=menu_servidor, daemon=True)
    menu_thread.start()
    aceitar_conexoes()