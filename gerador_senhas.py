import tkinter as tk # Importa o módulo tkinter para criar a inteface gráfica
from tkinter import messagebox # Importa a função messagebox para exibir mensagens
import random # Importa o módulo random para gerar senhas aleatórias
import string # Importa o módulo string para usar caracteres alfanuméricos e símbolos
import re # Importa o módulo de expressões regulares
import sqlite3 # Importa o módulo sqlite para integração com banco de dados
from cryptography.fernet import Fernet # Importa o módulo cryptography para trabalhar com criptografia
import os # Importa o módulo os para gerenciar arquivos
from datetime import datetime

# Define uma função que Gera chave
def gerar_chave():
    chave = Fernet.generate_key()
    with open('chave.key', 'wb') as chave_file:
        chave_file.write(chave)
    return chave

# Define uma função que Carrega a chave
def carregar_chave():
    chave = open('chave.key', 'rb').read()
    try:
        Fernet(chave)
        return chave
    except ValueError:
        return gerar_chave()

# Inicializar Fernet
chave = gerar_chave() if not os.path.exists('chave.key') else carregar_chave()
fernet = Fernet(chave)

# Define uma função para gerar senhas
def gerar_senha(tamanho):
    caracteres = string.ascii_letters + string.digits + string.punctuation # Conjunto de caracteres a ser usado na senha
    senha = ''.join(random.choice(caracteres) for _ in range(tamanho)) # Gera uma senha escolhendo caracteres aleatórios
    return senha # Retorna a senha gerada

# Função para validar se o nome contém apenas letras
def validar_nome(nome):
    if not nome.isalpha():
        messagebox.showerror('ERRO', 'O Nome do Usúario deve conter apenas letras')# Exibe uma mensagem de erro caso a condição não for satisfeita
        return False
    return True

# Função para validar se o serviço é um URL válido
def validar_servico(servico):
    pattern = re.compile(r'^(http|https)://') # Expressão Regular para URLs
    if not pattern.match(servico):
        messagebox.showerror('ERRO', 'Por Favor, insira uma URL válida') # Exibe uma mensagem de erro caso a condição não for satisfeita 
        return False
    return True

# Função para validar se o tamanho da senha é um número inteiro
def validar_tamanho(tamanho):
    if not tamanho.isdigit():
        messagebox.showerror('ERRO', 'O tamanho da senha deve ser um número inteiro') # Exibe uma mensagem de erro caso a condição não for satisfeita
        return False
    return True

# Função para criptografar senha
def criptografar_senha(senha):
    return fernet.encrypt(senha.encode())

# Função para descriptografar senha
def descriptografar_senha(senha_criptografada):
    return fernet.decrypt(senha_criptografada).decode()

# Função para salvar a senha gerada
def salvar_senha():
    servico = entrada_servico.get() # Obtém o nome do serviço a partir da entrada de texto
    usuario = entrada_usuario.get() # Obtém o nome do usuário a partir da entrada de texto
    tamanho = entrada_tamanho.get() # Obtém o tamanho da senha a partir da entrada de texto

    if not validar_nome(usuario): # Valida o nome do usuário
        return
    
    if not validar_servico(servico): # Valida o serviço
        return
    
    if not validar_tamanho(tamanho): # Valida o tamanho da senha
        return
    
    senha = gerar_senha(int(tamanho)) # Gera uma nova senha com o tamanho especificado
    senha_criptografada = criptografar_senha(senha)
    data_criacao = datetime.now().strftime('%Y-%m-%d')

    conn = sqlite3.connect('dados_senhas.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS senhas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        serviço TEXT NOT NULL,
        usuario TEXT NOT NULL,
        senha BLOB NOT NULL
    )''')

    cursor.execute('''
    INSERT INTO senhas(servico, usuario, senha) VALUES (?, ?, ?)
    ''', (servico, usuario, senha_criptografada))
    conn.commit()
    conn.close()

    # Exibe a senha gerada na interface
    entrada_senha.delete(0, tk.END) # Limpa o campo de entrada da senha
    entrada_senha.insert(0, senha) # Insere a senha gerada no campo de entrada

    messagebox.showinfo('Senha Salva', f'Senha para {servico} salva com sucesso') # Exibe uma mensagem de confirmação caso condição seja satisfeita

# Função para copiar a senha para a área de trensferência
def copiar_senha():
    senha = entrada_senha.get() # Obtém a senha gerada a partir do campo de entrada
    janela.clipboard_clear() # Limpa o conteúdo da área de trasferência
    janela.clipboard_append(senha) # Copia a senha para a área de transferência
    messagebox.showinfo('Senha Copiada', 'Senha copiada para a área de transferência') # Exibe uma mensagem de confirmação caso condição seja satisfeita

# Função para autenticar o usuário
def autenticar_usuario():
    senha_autenticacao = 'minhasenha' # Substitua pela sua senha de autenticação
    senha_digitada = entrada_autenticacao.get()
    if senha_digitada == senha_autenticacao:
        messagebox.showinfo('Autenticação Bem-Secedida', 'Usuário autenticado com sucesso.')
        listar_senhas() # Chama a função para  listar as senhas após autenticação
    else:
        messagebox.showerror('Erro de autenticação', 'Senha de autenticação incorreta')

# Função para listar senhas armazenadas no banco de dados após autenticação
def listar_senhas():
    conn = sqlite3.connect('dados_senhas.db')
    cursor = conn.cursor()
    cursor.execute('SELECT servico, usuario, senha FROM senhas')
    senhas = cursor.fetchall()
    conn.close()

    janela_listagem = tk.Toplevel()
    janela_listagem.title('Lista de Senhas')

    texto = tk.Text(janela_listagem, wrap='word')
    texto.pack(padx=10, pady=10, expand=True, fill='both')

    for servico, usuario, senha_criptografa in senhas:
        senha = descriptografar_senha(senha_criptografa)
        texto.insert(tk.END, f'Serviço: {servico}\nUsuário: {usuario}\nSenha: {senha}\n\n')

# Configuração da interface Tkinter
janela = tk.Tk() # Cria uma nova Tkinter
janela.title('Gerador de Senhas') # Define o título da janela

# Adiciona um frame para agrupar os campos
frame = tk.Frame(janela, padx=10, pady=10)
frame.grid(row=0, column=0, padx=10, pady=10)

# Criação dos rótulos e campos de entrada
tk.Label(frame, text='Serviço', font=('Arial', 12)).grid(row=0, column=0, padx=10, pady=5, sticky='w') # Adiciona um rótulo para o campo de serviço
entrada_servico = tk.Entry(frame, font=('Arial', 12)) # Cria uma entrada de texto para o nome do serviço
entrada_servico.grid(row=0, column=1, padx=10, pady=5) # Posiciona a entrada de texto na janela

tk.Label(frame, text='Usuário', font=('Arial', 12)).grid(row=1, column=0, padx=10, pady=5, sticky='w') # Adiciona um rótulo para o campo de usuário 
entrada_usuario = tk.Entry(frame, font=('Arial', 12)) # Cria uma entrada de texto para o nome do usuário
entrada_usuario.grid(row=1, column=1, padx=10, pady=5) # Posicione a entrada de texto na janela

tk.Label(frame, text='Tamanho da Senha', font=('Arial', 12)).grid(row=2, column=0, padx=10, pady=5, sticky='w') # Adiciona um rótulo para o campo de tamanho da senha
entrada_tamanho = tk.Entry(frame, font=('Arial', 12)) # Cria uma entrada de texto para o tamanho da senha
entrada_tamanho.grid(row=2, column=1, padx=10, pady=5) # Posiciona a entrada de texto na janela

tk.Label(frame, text='Senha Gerada', font=('Arial', 12)).grid(row=4, column=0, padx=10, pady=5, sticky='w') # Adiciona um rótulo para o campo da senha gerada
entrada_senha = tk.Entry(frame, font=('Arial', 12)) # Cria uma entrada de texto para exibir a senha gerada
entrada_senha.grid(row=4, column=1, padx=10, pady=5) # Posiciona a entrada de texto na janela

# Campo de entrada para a senha de autenticação
tk.Label(frame, text='Senha de Autenticação', font=('Arial', 12)).grid(row=6, column=0, padx=10, pady=5, sticky='w')
entrada_autenticacao = tk.Entry(frame, font=('Arial', 12), show='*') # O parâmetro show='*' oculta a senha digitada
entrada_autenticacao.grid(row=6, column=1, padx=10, pady=5)

tk.Button(frame, text='Gerar e Salvar Senha', command=salvar_senha, font=('Arial', 12), bg='#4CAF50', fg='white').grid(row=3, column=1, padx=10, pady=10)

# Adiciona um botão que chama a função copiar_senha ao ser clicado
tk.Button(frame, text='Copiar Senha', command=copiar_senha, font=('Arial', 12), bg='#2196F3', fg='white').grid(row=5, column=1, padx=10, pady=10)

tk.Button(frame, text='Autenticar e Listar Senhas', command=autenticar_usuario, font=('Arial', 12), bg='#FFC107', fg='black').grid(row=7, column=1, padx=10, pady=10)

janela.mainloop() # Inicia o loop principal da interface, mantendo a janela aberta