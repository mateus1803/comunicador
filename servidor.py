import socket
import tkinter as tk
from threading import Thread

class ServidorAvisos:
    def __init__(self, endereco_servidor, porta_servidor):
        self.endereco_servidor = endereco_servidor
        self.porta_servidor = porta_servidor
        self.clientes = []
        self.mensagens = {}  # Dicionário para armazenar mensagens {id_mensagem: mensagem}
        self.id_mensagem = 1  # Identificador único para cada mensagem
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_servidor.bind((self.endereco_servidor, self.porta_servidor))
        self.socket_servidor.listen(5)
        print("Servidor de Avisos iniciado.")
        self.aceitar_conexoes()

    def aceitar_conexoes(self):
        while True:
            cliente, endereco_cliente = self.socket_servidor.accept()
            self.clientes.append(cliente)
            print(f"Conexão estabelecida com {endereco_cliente}.")
            Thread(target=self.ler_mensagens_cliente, args=(cliente,)).start()

    def ler_mensagens_cliente(self, cliente):
        while True:
            try:
                mensagem = cliente.recv(1024).decode("utf-8")
                if mensagem:
                    print("Mensagem recebida:", mensagem)
                    if mensagem.startswith("editar:"):
                        self.editar_mensagem(mensagem)
                    elif mensagem.startswith("apagar:"):
                        self.apagar_mensagem(mensagem)
                    else:
                        self.enviar_aviso(mensagem)
                else:
                    cliente.close()
                    self.clientes.remove(cliente)
                    break
            except:
                continue

    def editar_mensagem(self, mensagem):
        comando, id_mensagem, nova_mensagem = mensagem.split(":")
        id_mensagem = int(id_mensagem)
        self.mensagens[id_mensagem] = nova_mensagem
        mensagem_atualizada = f"mensagens:{id_mensagem}|{nova_mensagem}"
        for cliente in self.clientes:
            cliente.send(mensagem_atualizada.encode("utf-8"))

    def apagar_mensagem(self, mensagem):
        comando, id_mensagem = mensagem.split(":")
        id_mensagem = int(id_mensagem)
        del self.mensagens[id_mensagem]
        mensagem_apagada = f"apagar:{id_mensagem}"
        for cliente in self.clientes:
            cliente.send(mensagem_apagada.encode("utf-8"))

    def enviar_aviso(self, aviso):
        id_mensagem = self.id_mensagem
        self.mensagens[id_mensagem] = aviso
        mensagem_enviada = f"mensagens:{id_mensagem}|{aviso}"
        self.id_mensagem += 1
        for cliente in self.clientes:
            cliente.send(mensagem_enviada.encode("utf-8"))


if __name__ == "__main__":
    endereco_servidor = "192.168.1.43"  # Endereço IP do servidor na rede local
    porta_servidor = 8888  # Porta para comunicação
    servidor = ServidorAvisos(endereco_servidor, porta_servidor)
