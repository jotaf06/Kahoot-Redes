from tkinter import *
from tkinter import font, ttk, scrolledtext

perguntas = ['Pergunta 1: Qual é a capital do Brasil?', 
             'Pergunta 2: Quantos planetas existem no sistema solar?',
             'Pergunta 3: Qual é o maior mamífero do mundo?',
             'Pergunta 4: Quem pintou a Mona Lisa?']

root = Tk()
root.title("Aplicativo Multi-funcional")
root.geometry("600x600")
root.config(background='#f0f0f0')

# Criando o notebook (aba)
notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True)

# ABA 1 - QUESTIONÁRIO
frame_questionario = Frame(notebook, background='#f0f0f0')
notebook.add(frame_questionario, text="Questionário")

# Frame principal centralizado
main_frame = Frame(frame_questionario, background='#f0f0f0')
main_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

# Questionário
text_frame = Frame(main_frame, background='#f0f0f0')
text_frame.pack(fill=BOTH, pady=(0, 20))

custom_font = font.Font(family='Poppins', size=12)
for i, pergunta in enumerate(perguntas, 1):
    Label(text_frame, 
          text=f'{pergunta}', 
          font=custom_font, 
          background='#f0f0f0',
          anchor='w',
          wraplength=480
          ).pack(fill=X, pady=5)

Label(main_frame, 
      text='Escolha sua resposta (1-4):', 
      font=custom_font, 
      background='#f0f0f0'
      ).pack(anchor='w', pady=(10, 5))

options_frame = Frame(main_frame, background='#f0f0f0')
options_frame.pack(fill=BOTH, pady=(0, 20))

selected_option = IntVar()
options = [("Opção 1", 1), ("Opção 2", 2), ("Opção 3", 3), ("Opção 4", 4)]

for i, (text, value) in enumerate(options):
    rb = ttk.Radiobutton(
        options_frame,
        text=text,
        variable=selected_option,
        value=value,
        style='TRadiobutton'
    )
    rb.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='w')

button_frame = Frame(main_frame, background='#f0f0f0')
button_frame.pack(fill=X, pady=(20, 0))

submit_btn = ttk.Button(
    button_frame,
    text='ENVIAR RESPOSTAS',
    style='TButton'
)
submit_btn.pack(fill=X)

# ABA 2 - CHAT
frame_chat = Frame(notebook, background='#f0f0f0')
notebook.add(frame_chat, text="Chat")

# Frame principal do chat centralizado
chat_main_frame = Frame(frame_chat, background='#f0f0f0')
chat_main_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

# Área de exibição das mensagens
chat_display = scrolledtext.ScrolledText(
    chat_main_frame,
    wrap=WORD,
    width=50,
    height=20,
    font=('Poppins', 10),
    bg='white'
)
chat_display.pack(pady=(0, 10))
chat_display.config(state=DISABLED)  # Impede edição direta

# Frame para entrada de mensagem e botão
input_frame = Frame(chat_main_frame, background='#f0f0f0')
input_frame.pack(fill=X)

# Campo de entrada de mensagem
message_entry = Entry(
    input_frame,
    font=('Poppins', 12),
    bg='white'
)
message_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
message_entry.bind('<Return>', lambda e: send_message())  # Enviar com Enter

# Botão de enviar
send_button = ttk.Button(
    input_frame,
    text="Enviar",
    command=lambda: send_message(),
    style='TButton'
)
send_button.pack(side=RIGHT)

def send_message():
    message = message_entry.get()
    if message.strip():  # Verifica se não está vazio
        # Habilita a edição temporária para adicionar a mensagem
        chat_display.config(state=NORMAL)
        chat_display.insert(END, f"Você: {message}\n")
        chat_display.config(state=DISABLED)
        
        # Adiciona o "eco" (resposta simulada)
        chat_display.config(state=NORMAL)
        chat_display.insert(END, f"Eco: {message}\n")
        chat_display.config(state=DISABLED)
        
        # Rolagem automática para a última mensagem
        chat_display.see(END)
        message_entry.delete(0, END)  # Limpa o campo de entrada

root.mainloop()