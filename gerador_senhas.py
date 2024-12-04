import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import random
import string
import re
import os  # Certifique-se de importar 'os'
from cryptography.fernet import Fernet  # Certifique-se de importar 'Fernet'
from db_utils import criar_tabela, salvar_senha, listar_senhas, excluir_senha
from crypto_utils import gerar_chave, carregar_chave, criptografar_senha, descriptografar_senha

# Inicializar Fernet
chave = gerar_chave() if not os.path.exists('chave.key') else carregar_chave()
fernet = Fernet(chave)

def gerar_senha(tamanho):
    caracteres = string.ascii_letters + string.digits + string.punctuation
    senha = ''.join(random.choice(caracteres) for _ in range(tamanho))
    return senha

def validar_nome(nome):
    if not nome.isalpha():
        messagebox.showerror('ERRO', 'O Nome do Usúario deve conter apenas letras')
        return False
    return True

def validar_servico(servico):
    pattern = re.compile(r'^(http|https)://')
    if not pattern.match(servico):
        messagebox.showerror('ERRO', 'Por Favor, insira uma URL válida')
        return False
    return True

def validar_tamanho(tamanho):
    if not tamanho.isdigit():
        messagebox.showerror('ERRO', 'O tamanho da senha deve ser um número inteiro')
        return False
    return True

def salvar_senha_gui():
    servico = entrada_servico.get()
    usuario = entrada_usuario.get()
    tamanho = entrada_tamanho.get()

    if not validar_nome(usuario):
        return
    
    if not validar_servico(servico):
        return
    
    if not validar_tamanho(tamanho):
        return
    
    senha = gerar_senha(int(tamanho))
    senha_criptografada = criptografar_senha(senha, fernet)
    salvar_senha(servico, usuario, senha_criptografada)

    entrada_senha.delete(0, tk.END)
    entrada_senha.insert(0, senha)
    messagebox.showinfo('Senha Salva', f'Senha para {servico} salva com sucesso')

def copiar_senha():
    senha = entrada_senha.get()
    janela.clipboard_clear()
    janela.clipboard_append(senha)
    messagebox.showinfo('Senha Copiada', 'Senha copiada para a área de transferência')

def autenticar_usuario():
    senha_autenticacao = 'minhasenha'
    senha_digitada = entrada_autenticacao.get()
    if senha_digitada == senha_autenticacao:
        messagebox.showinfo('Autenticação Bem-Sucedida', 'Usuário autenticado com sucesso.')
        listar_senhas_gui()
    else:
        messagebox.showerror('Erro de autenticação', 'Senha de autenticação incorreta')

def listar_senhas_gui():
    senhas = listar_senhas()

    janela_listagem = tk.Toplevel()
    janela_listagem.title('Lista de Senhas')

    texto = tk.Text(janela_listagem, wrap='word')
    texto.pack(padx=10, pady=10, expand=True, fill='both')

    for servico, usuario, senha_criptografada in senhas:
        senha = descriptografar_senha(senha_criptografada, fernet)
        texto.insert(tk.END, f'Serviço: {servico}\nUsuário: {usuario}\nSenha: {senha}\n')
        tk.Button(janela_listagem, text='Excluir', command=lambda s=servico, u=usuario: excluir_senha(s, u)).pack(pady=2)
        texto.insert(tk.END, '\n')

def estilizar_interface():
    style = ttk.Style()
    style.configure('TButton', font=('Arial', 12), background='#4CAF50', foreground='white', padding=10)
    style.configure('TLabel', font=('Arial', 12))
    style.configure('TEntry', font=('Arial', 12))

# Configuração da interface Tkinter
janela = tk.Tk()
janela.title('Gerenciador de Contas e Senhas')
janela.geometry('450x550')

estilizar_interface()

# Adiciona um frame para agrupar os campos
frame = ttk.Frame(janela, padding="10 10 10 10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Permitir redimensionamento automático
janela.columnconfigure(0, weight=1)
janela.rowconfigure(0, weight=1)

# Criação dos rótulos e campos de entrada
ttk.Label(frame, text='Serviço').grid(row=0, column=0, padx=10, pady=5, sticky='w')
entrada_servico = ttk.Entry(frame)
entrada_servico.grid(row=0, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))

ttk.Label(frame, text='Usuário').grid(row=1, column=0, padx=10, pady=5, sticky='w')
entrada_usuario = ttk.Entry(frame)
entrada_usuario.grid(row=1, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))

ttk.Label(frame, text='Tamanho da Senha').grid(row=2, column=0, padx=10, pady=5, sticky='w')
entrada_tamanho = ttk.Entry(frame)
entrada_tamanho.grid(row=2, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))

ttk.Label(frame, text='Senha Gerada').grid(row=4, column=0, padx=10, pady=5, sticky='w')
entrada_senha = ttk.Entry(frame)
entrada_senha.grid(row=4, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))

ttk.Label(frame, text='Senha de Autenticação').grid(row=6, column=0, padx=10, pady=5, sticky='w')
entrada_autenticacao = ttk.Entry(frame, show='*')
entrada_autenticacao.grid(row=6, column=1, padx=10, pady=5, sticky=(tk.W, tk.E))

ttk.Button(frame, text='Gerar e Salvar Senha', command=salvar_senha_gui).grid(row=3, column=1, padx=10, pady=10)
ttk.Button(frame, text='Copiar Senha', command=copiar_senha).grid(row=5, column=1, padx=10, pady=10)
ttk.Button(frame, text='Autenticar e Listar Senhas', command=autenticar_usuario).grid(row=7, column=1, padx=10, pady=10)

# Permitir redimensionamento automático dos widgets dentro do frame
for child in frame.winfo_children():
    child.grid_configure(sticky=(tk.W, tk.E))

janela.mainloop()
