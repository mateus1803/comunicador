import socket
import tkinter as tk
from tkinter import simpledialog
import threading

endereco_servidor = "192.168.1.43"  # Endereço IP do servidor na rede local
porta_servidor = 8888  # Porta para comunicação

def enviar_mensagem():
    aviso = entrada_aviso.get()
    socket_cliente.send(aviso.encode("utf-8"))
    entrada_aviso.delete(0, tk.END)  # Limpa a entrada de texto após o envio da mensagem

def editar_mensagem():
    mensagem_selecionada = texto_mensagens.tag_ranges("sel")
    if mensagem_selecionada:
        inicial, final = mensagem_selecionada
        mensagem = texto_mensagens.get(inicial, final)
        id_mensagem, texto_mensagem = mensagem.split(": ", 1)
        nova_mensagem = simpledialog.askstring("Editar Mensagem", "Digite a nova mensagem:", initialvalue=texto_mensagem)
        if nova_mensagem:
            nova_mensagem_formatada = f"{id_mensagem}: {nova_mensagem}"
            texto_mensagens.delete(inicial, final)
            texto_mensagens.insert(inicial, nova_mensagem_formatada)
            socket_cliente.send(f"editar:{id_mensagem}:{nova_mensagem}".encode("utf-8"))

def apagar_mensagem():
    mensagem_selecionada = texto_mensagens.tag_ranges("sel")
    if mensagem_selecionada:
        inicial, final = mensagem_selecionada
        mensagem = texto_mensagens.get(inicial, final)
        id_mensagem, _ = mensagem.split(": ", 1)
        socket_cliente.send(f"apagar:{id_mensagem}".encode("utf-8"))
        texto_mensagens.delete(inicial, final)

def atualizar_lista_mensagens():
    texto_mensagens.delete("1.0", tk.END)
    for id_mensagem, mensagem in mensagens:
        texto_mensagens.insert(tk.END, f"{id_mensagem}: {mensagem}\n")

def receber_mensagens():
    while True:
        mensagem = socket_cliente.recv(1024).decode("utf-8")
        if mensagem:
            print("Mensagem recebida:", mensagem)
            if mensagem.startswith("mensagens:"):
                mensagens.clear()
                mensagem_data = mensagem.split(":")[1:]
                for mensagem_item in mensagem_data:
                    id_mensagem, texto_mensagem = mensagem_item.split("|")
                    mensagens.append((id_mensagem, texto_mensagem))
                atualizar_lista_mensagens()
            else:
                texto_mensagens.insert(tk.END, mensagem + "\n")  # Adiciona a mensagem ao Text do administrador

socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_cliente.connect((endereco_servidor, porta_servidor))

mensagens = []  # Lista para armazenar mensagens

# Configuração da janela
janela = tk.Tk()
janela.title("Administrador de Avisos")

# Adiciona entrada de texto para digitar a mensagem
entrada_aviso = tk.Entry(janela, width=50)
entrada_aviso.grid(row=0, column=0, padx=10, pady=10)

# Adiciona botão para enviar a mensagem
botao_enviar = tk.Button(janela, text="Enviar", command=enviar_mensagem)
botao_enviar.grid(row=0, column=1, padx=10, pady=10)

# Área de exibição das mensagens
texto_mensagens = tk.Text(janela, width=60, height=10)
texto_mensagens.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Adiciona botão para editar a mensagem
botao_editar = tk.Button(janela, text="Editar Mensagem", command=editar_mensagem)
botao_editar.grid(row=2, column=0, padx=10, pady=10)

# Adiciona botão para apagar a mensagem
botao_apagar = tk.Button(janela, text="Apagar Mensagem", command=apagar_mensagem)
botao_apagar.grid(row=2, column=1, padx=10, pady=10)

# Inicia uma thread para receber mensagens do servidor
thread_receber_mensagens = threading.Thread(target=receber_mensagens)
thread_receber_mensagens.start()

janela.mainloop()

socket_cliente.close()
