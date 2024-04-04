import tkinter as tk
from tkinter import scrolledtext
import socket
import threading
from datetime import datetime, timedelta
import os

class ClienteGUI:
    def __init__(self, endereco_servidor, porta_servidor):
        self.endereco_servidor = endereco_servidor
        self.porta_servidor = porta_servidor
        self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_cliente.connect((self.endereco_servidor, self.porta_servidor))

        # Configuração da janela
        self.janela = tk.Tk()
        self.janela.title("Cliente de Avisos")
        
        # Configuração da área de mensagens
        self.area_mensagens = scrolledtext.ScrolledText(self.janela, width=60, height=20)
        self.area_mensagens.pack(padx=10, pady=10)

        # Botão para limpar mensagens
        self.botao_limpar = tk.Button(self.janela, text="Limpar Mensagens", command=self.limpar_mensagens)
        self.botao_limpar.pack(padx=10, pady=5)

        # Bloqueia a entrada de texto
        self.area_mensagens.bind("<Key>", lambda e: "break")

        # Dicionário para rastrear mensagens e seus horários de recebimento
        self.mensagens = {}

        # Carrega mensagens anteriores
        self.carregar_mensagens()

        # Inicia uma thread para receber mensagens do servidor
        thread_receber_mensagens = threading.Thread(target=self.receber_mensagens)
        thread_receber_mensagens.start()

        # Inicia temporizador para limpar mensagens
        self.iniciar_temporizador()

    def carregar_mensagens(self):
        try:
            with open("mensagens.txt", "r") as arquivo:
                mensagens = arquivo.readlines()
                for mensagem in mensagens:
                    self.area_mensagens.insert(tk.END, mensagem)
                    # Adiciona mensagem ao dicionário com o horário de recebimento atual
                    self.mensagens[mensagem.strip()] = datetime.now()
        except FileNotFoundError:
            print("Arquivo de mensagens não encontrado.")

    def receber_mensagens(self):
        while True:
            mensagem = self.socket_cliente.recv(1024).decode("utf-8")
            if mensagem:
                data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                mensagem_formatada = f"[{data_hora}] {mensagem}\n"
                self.area_mensagens.insert(tk.END, mensagem_formatada)
                self.salvar_mensagem(mensagem_formatada)
                # Adiciona mensagem ao dicionário com o horário de recebimento atual
                self.mensagens[mensagem_formatada.strip()] = datetime.now()

    def salvar_mensagem(self, mensagem):
        with open("mensagens.txt", "a") as arquivo:
            arquivo.write(mensagem)

    def limpar_mensagens(self):
        self.area_mensagens.delete(1.0, tk.END)
        # Limpa também o conteúdo do arquivo mensagens.txt
        with open("mensagens.txt", "w") as arquivo:
            arquivo.truncate(0)

    def iniciar_temporizador(self):
        # Define temporizador para verificar e limpar mensagens a cada minuto
        threading.Timer(60, self.verificar_limpeza_mensagens).start()

    def verificar_limpeza_mensagens(self):
        agora = datetime.now()
        mensagens_para_remover = []
        for mensagem, horario_recebimento in self.mensagens.items():
            if agora - horario_recebimento > timedelta(hours=12):
                mensagens_para_remover.append(mensagem)

        # Remove mensagens da área de mensagens, do arquivo de mensagens e do dicionário de mensagens
        for mensagem in mensagens_para_remover:
            self.area_mensagens.delete('1.0', tk.END)
            self.remover_mensagem_arquivo("mensagens.txt", mensagem)
            del self.mensagens[mensagem]

        # Agenda a próxima verificação
        threading.Timer(60, self.verificar_limpeza_mensagens).start()

    def remover_mensagem_arquivo(self, arquivo, mensagem):
        # Lê todas as mensagens do arquivo
        with open(arquivo, "r") as f:
            linhas = f.readlines()

        # Abre o arquivo para reescrever, excluindo as mensagens antigas
        with open(arquivo, "w") as f:
            for linha in linhas:
                if linha.strip() != mensagem.strip():
                    f.write(linha)

    def iniciar(self):
        self.janela.mainloop()
        self.socket_cliente.close()

if __name__ == "__main__":
    endereco_servidor = "192.168.1.43"  # Endereço IP do servidor na rede local
    porta_servidor = 8888  # Porta para comunicação
    cliente = ClienteGUI(endereco_servidor, porta_servidor)
    cliente.iniciar()
