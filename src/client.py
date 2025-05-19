import socket
import json
import os
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox
from dotenv import load_dotenv

load_dotenv(override=True)

HOST = os.getenv("SERVER_IP", "localhost")
PORT = int(os.getenv("SERVER_PORT", 12345))

class ClientApp:
    def __init__(self, master):
        self.master      = master
        self.sock        = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.nick = simpledialog.askstring("Nickname", "Digite seu nickname:", parent=master)
        if not self.nick:
            master.destroy()
            return

        try:
            self.sock.connect((HOST, PORT))
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível conectar: {e}")
            master.destroy()
            return

        self.sock.send(self.nick.encode('utf-8'))

        # cria GUI
        master.title("Chat & Kahoot Cliente")
        master.geometry("600x600")
        nb = ttk.Notebook(master)
        nb.pack(fill=tk.BOTH, expand=True)

        # aba kahoot
        self.frame_kahoot = ttk.Frame(nb)
        nb.add(self.frame_kahoot, text="Kahoot")
        self._build_kahoot_ui()

        # aba chat
        self.frame_chat = ttk.Frame(nb)
        nb.add(self.frame_chat, text="Chat")
        self._build_chat_ui()
        self._append_chat(f'{self.nick} entrou na sala!')

        # thread de recepção
        threading.Thread(target=self.receive_loop, daemon=True).start()

    def _build_chat_ui(self):
        self.chat_display = scrolledtext.ScrolledText(self.frame_chat, state=tk.DISABLED)
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        entry_frame = ttk.Frame(self.frame_chat)
        entry_frame.pack(fill=tk.X, padx=5, pady=5)
        self.msg_entry = ttk.Entry(entry_frame)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.msg_entry.bind("<Return>", lambda e: self.send_chat())
        self.send_btn = ttk.Button(entry_frame, text="Enviar", command=self.send_chat)
        self.send_btn.pack(side=tk.RIGHT)

    def _build_kahoot_ui(self):
        self.question_lbl = ttk.Label(self.frame_kahoot, text="", wraplength=500, font=("Arial", 12))
        self.question_lbl.pack(pady=10)
        self.opt_var = tk.IntVar(value=0)
        self.rbs = []
        for i in range(4):
            rb = ttk.Radiobutton(self.frame_kahoot, text=f"Opção {i+1}", variable=self.opt_var, value=i+1)
            rb.pack(anchor=tk.W, padx=20, pady=2)
            rb.config(state=tk.DISABLED)
            self.rbs.append(rb)
        self.submit_btn = ttk.Button(self.frame_kahoot, text="Enviar resposta", command=self.send_answer, state=tk.DISABLED)
        self.submit_btn.pack(pady=10)
        self.feedback_lbl = ttk.Label(self.frame_kahoot, text="")
        self.feedback_lbl.pack(pady=10)

    def send_chat(self):
        msg = self.msg_entry.get().strip()
        if not msg:
            return
        if msg.lower() == "/sair":
            self.sock.send(msg.encode('utf-8'))
            self.master.destroy()
            return
        self._append_chat(f'{self.nick}: {msg}')
        self.sock.send(msg.encode('utf-8'))
        self.msg_entry.delete(0, tk.END)

    def send_answer(self):
        choice = self.opt_var.get()
        if choice < 1 or choice > 4:
            return
        self.sock.send(str(choice).encode('utf-8'))
        self._set_kahoot_state(active=False)
        self.feedback_lbl.config(text="Resposta enviada! Aguarde...")

    def _set_chat_state(self, active: bool):
        state = tk.NORMAL if active else tk.DISABLED
        self.msg_entry.config(state=state)
        self.send_btn.config(state=state)

    def _set_kahoot_state(self, active: bool):
        state = tk.NORMAL if active else tk.DISABLED
        for rb in self.rbs:
            rb.config(state=state)
        self.submit_btn.config(state=state)
        self._set_chat_state(active=not active)
        if not active:
            self.opt_var.set(0)

    def receive_loop(self):
        while True:
            try:
                data = self.sock.recv(4096).decode('utf-8')
                if not data:
                    break
                try:
                    msg = json.loads(data)
                except json.JSONDecodeError:
                    self._append_chat(data)
                    continue

                mtype = msg.get('type')
                if mtype == 'history':
                    for line in msg['messages']:
                        self._append_chat(line)
                elif mtype == 'question':
                    self._set_kahoot_state(active=True)
                    self.feedback_lbl.config(text="")
                    self.question_lbl.config(text=msg['question'])
                    for i, opt in enumerate(msg['options']):
                        self.rbs[i].config(text=opt)
                elif mtype == 'feedback':
                    correct = msg['correct'] + 1
                    scores = msg['scores']
                    fb = f"Resposta correta: {correct}\n"
                    for nick, sc in scores.items():
                        fb += f"{nick}: {sc}\n"
                    self.feedback_lbl.config(text=fb)
                else:
                    self._append_chat(data)

            except ConnectionResetError:
                break

    def _append_chat(self, text: str):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, text + "\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app  = ClientApp(root)
    root.mainloop()
