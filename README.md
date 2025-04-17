# WebChat-Redes

Projeto para a disciplina de Redes de Computadores do curso de Engenharia de Computação (UFAL).

## Integrantes da Equipe

- José Félix  
- Efraim Lopes  
- Kauã Lessa  

## Descrição do Projeto

O WebChat-Redes é um sistema de chat em grupo utilizando sockets e threads, desenvolvido em Python. A aplicação permite que múltiplos clientes se conectem simultaneamente a um servidor e troquem mensagens em tempo real.

O servidor permanece em execução e escuta conexões indefinidamente. Cada cliente pode enviar mensagens ao grupo ou sair do chat com o comando `/sair`.

## Funcionalidades

- Envio e recebimento de mensagens entre vários clientes.
- Cada cliente utiliza um nickname exclusivo.
- Mensagens são transmitidas para todos os participantes (exceto quem enviou).
- Tratamento de desconexão com aviso aos demais usuários.
- Threads são utilizadas para manter o servidor responsivo a múltiplas conexões simultâneas.

## Requisitos

- Python 3.6 ou superior

## Como Executar

### 1. Clone o repositório (ou copie os arquivos)
Certifique-se de que `server.py` e `client.py` estão no mesmo diretório.

### 2. Execute o servidor

```bash
python3 server.py
```

O terminal deve exibir:  
`Servidor escutando na porta 12345`

### 3. Execute os clientes (em diferentes terminais)

```bash
python3 client.py
```

Digite seu nickname quando solicitado. Você pode executar esse comando em quantas janelas de terminal quiser para simular múltiplos usuários.

### 4. Comandos disponíveis

- `/sair` — Encerra a conexão do cliente com o chat.

## Exemplo de Uso

1. Três terminais são abertos: um servidor, dois clientes.
2. Cliente 1 digita: `Oi, pessoal!`
3. Cliente 2 vê a mensagem e responde: `E aí!`
4. Cliente 1 digita: `/sair`
5. Todos veem a mensagem: `Cliente1 saiu do chat!`

## Observações

- O servidor deve ser encerrado manualmente com `Ctrl+C`.
- Caso ocorra erro de "mensagens vazias" ou falhas após desconexões, verifique se a versão do código está atualizada.
- A comunicação é feita exclusivamente na máquina local (localhost). Para rodar em diferentes computadores, é necessário configurar o IP local do servidor.

## Licença

Uso educacional para fins de aprendizado na disciplina de Redes de Computadores.