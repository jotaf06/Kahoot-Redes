# Kahoot-Redes

## Sumário

- [Integrantes da Equipe](#integrantes-da-equipe)
- [Descrição do Projeto](#descrição-do-projeto)
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Configuração de Variáveis de Ambiente](#configuração-de-variáveis-de-ambiente)
- [Como Executar](#como-executar)
    - [1. Clone o repositório (ou copie os arquivos)](#1-clone-o-repositório-ou-copie-os-arquivos)
    - [2. Crie um ambiente virtual Python e instale as dependências](#2-crie-um-ambiente-virtual-python-e-instale-as-dependências)
    - [3. Execute o servidor](#3-execute-o-servidor)
    - [4. Execute os clientes (em diferentes terminais)](#4-execute-os-clientes-em-diferentes-terminais)
    - [5. Comandos disponíveis](#5-comandos-disponíveis)
- [Exemplo de Uso](#exemplo-de-uso)
- [Observações](#observações)
- [Licença](#licença)

## Integrantes da Equipe

- José Félix  
- Efraim Lopes  
- Kauã Lessa
- Plácido Cordeiro

## Descrição do Projeto

O WebChat-Redes é um sistema de chat em grupo utilizando sockets e threads, desenvolvido em Python. A aplicação permite que múltiplos clientes se conectem simultaneamente a um servidor e troquem mensagens em tempo real.

O servidor permanece em execução e escuta conexões indefinidamente. Cada cliente pode enviar mensagens ao grupo ou sair do chat com o comando `/sair`.

## Funcionalidades

- Envio e recebimento de mensagens entre vários clientes.
- Cada cliente utiliza um nickname exclusivo.
- Mensagens são transmitidas para todos os participantes.
- Tratamento de desconexão com aviso aos demais usuários.
- Threads são utilizadas para manter o servidor responsivo a múltiplas conexões simultâneas.

## Requisitos

- Python 3.6 ou superior
- Dependências do `requirements.txt`

## Configuração de Variáveis de Ambiente

Para o funcionamento correto do projeto, é necessário configurar as variáveis de ambiente no arquivo `.env`, seguindo o padrão do arquivo `.env.example`. Certifique-se de definir a porta e o endereço IP da máquina que atuará como servidor, de acordo com a rede de internet em que ela estiver conectada.

## Como Executar

### 1. Clone o repositório (ou copie os arquivos)
Certifique-se de que `server.py` e `client.py` estão no mesmo diretório.

### 2. Crie um ambiente virtual Python e instale as dependências

No diretório do projeto, execute:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Execute o servidor

```bash
python3 server.py
```

O terminal deve exibir:  
`Servidor escutando na porta 12345`

### 4. Execute os clientes (em diferentes terminais)

```bash
python3 client.py
```

Digite seu nickname quando solicitado. Você pode executar esse comando em quantas janelas de terminal quiser para simular múltiplos usuários.

O projeto também funciona para diferentes máquinas conectadas à mesma rede de internet, desde que todas estejam com o arquivo `.env` devidamente configurado, especificando corretamente o IP do servidor e a porta utilizada.

### 5. Comandos disponíveis

#### No servidor (terminal):

- `/sair` — Encerra o servidor e desconecta todos os clientes.
- `/iniciar` — Inicia o quiz, desde que pelo menos dois clientes estejam conectados.

#### No cliente:

- O usuário pode digitar mensagens normalmente no chat.
- Quando o quiz for iniciado pelo servidor, aparecerão perguntas na tela para serem respondidas diretamente pelo cliente.
- O comando `/sair` também pode ser usado para o cliente sair do chat.

## Exemplo de Uso

1. Três terminais são abertos: um servidor, dois clientes.
2. Cliente 1 digita: `Oi, pessoal!`
3. Cliente 2 vê a mensagem e responde: `E aí!`
4. Cliente 1 digita: `/sair`
5. Todos veem a mensagem: `Cliente1 saiu do chat!`

## Observações

- O servidor deve ser encerrado manualmente com o comando `/sair` ou `Ctrl+C`.
- Caso ocorra erro de "mensagens vazias" ou falhas após desconexões, verifique se a versão do código está atualizada.
- O aplicativo funciona em diferentes máquinas conectadas à mesma rede, desde que o IP do servidor esteja corretamente configurado no arquivo `.env` dos clientes. Caso o IP não seja configurado corretamente, a comunicação ocorrerá apenas localmente (localhost).

## Licença

Uso educacional para fins de aprendizado na disciplina de Redes de Computadores.
